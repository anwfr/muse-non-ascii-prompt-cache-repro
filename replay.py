"""Replay recorded Claude Code requests to Muse, in order, and report how much of each previous request is read from cache.

Run:  API_KEY=<Muse key> python3 replay.py <claude-code run folder> <out-dir> [as-is|ascii-tools]
Needs Python 3 only. Costs a few cents on Muse.

The run folder is one of runs/claude-code_muse_*: its requests/NN.request.json are the bodies Claude Code sent.
Only the conversation requests (those carrying tools) are replayed, in order, with a new tag at the start of the
system prompt so that nothing cached by an earlier replay can help. `metadata` is always dropped (it is not
prompt text). Variants:

  as-is         nothing else changed
  ascii-tools   the non-ASCII characters of the tool descriptions replaced by ASCII (an em dash becomes "-");
                names, types, enums and schemas unchanged (see ascii_tools.py)

Writes into <out-dir>: output.txt (one line per request, with its x-request-id and time), and
requests/NN.request.json (exact body sent) and NN.response.json (status, headers, raw response) for each request.
"""
import json, os, pathlib, sys, time, urllib.error, urllib.request, uuid

from ascii_tools import fold_descriptions

URL = "https://api.meta.ai/v1/messages"
VARIANTS = ("as-is", "ascii-tools")


def mutate(body, variant, tag):
    b = json.loads(json.dumps(body))
    b.pop("metadata", None)
    b["max_tokens"] = 64
    if isinstance(b.get("system"), list) and b["system"]:
        b["system"][0]["text"] = "Replay %s. %s" % (tag, b["system"][0]["text"])
    if variant == "ascii-tools":
        b["tools"] = fold_descriptions(b["tools"])
    return b


def usage_of(raw, streamed):
    if not streamed:
        return json.loads(raw).get("usage") or {}
    u = {}
    for line in raw.splitlines():
        if line.startswith("data:"):
            try:
                e = json.loads(line[5:])
            except ValueError:
                continue
            if e.get("type") == "message_start":
                u.update((e.get("message") or {}).get("usage") or {})
            elif e.get("type") == "message_delta":
                u.update({k: v for k, v in (e.get("usage") or {}).items() if v is not None})
    return u


def main():
    if len(sys.argv) < 3 or (sys.argv[3:] and sys.argv[3] not in VARIANTS):
        sys.exit("usage: python3 replay.py <claude-code run folder> <out-dir> [%s]" % "|".join(VARIANTS))
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    variant = sys.argv[3] if sys.argv[3:] else "as-is"
    key = os.environ["API_KEY"]
    bodies = [json.loads(f.read_text())["body"] for f in sorted((src / "requests").glob("*.request.json"))]
    bodies = [b for b in bodies if b.get("tools") and "safeguards" not in b]  # conversation requests Muse accepted
    (out / "requests").mkdir(parents=True, exist_ok=True)
    tag = uuid.uuid4().hex[:8]
    lines = ["Replay of %s to Muse, variant %s, tag %s" % (src.name, variant, tag), "",
             "Expected from the second request on: 100% of the previous request read from cache.", ""]
    previous = None
    for n, body in enumerate(bodies, 1):
        b = mutate(body, variant, tag)
        raw_body = json.dumps(b, ensure_ascii=False)
        (out / "requests" / ("%02d.request.json" % n)).write_text(raw_body)
        headers = {"anthropic-version": "2023-06-01", "content-type": "application/json"}
        req = urllib.request.Request(URL, raw_body.encode(), dict(headers, **{"x-api-key": key}))
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    status, rh, raw = r.status, dict(r.headers.items()), r.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as e:
                status, rh, raw = e.code, dict(e.headers.items()), e.read().decode("utf-8", "replace")
                break
            except (urllib.error.URLError, OSError):
                time.sleep(10)
        else:
            sys.exit("no connection after 3 attempts")
        (out / "requests" / ("%02d.response.json" % n)).write_text(json.dumps(
            {"url": URL, "request_headers": dict(headers, **{"x-api-key": "<redacted>"}), "status": status,
             "response_headers": rh, "response_raw": raw}, indent=1, ensure_ascii=False))
        h = {k.lower(): v for k, v in rh.items()}
        if status != 200:
            lines.append("  %02d  refused, HTTP %d: %s" % (n, status, raw[:300]))
            break
        u = usage_of(raw, b.get("stream"))
        read = u.get("cache_read_input_tokens") or 0
        sent = read + (u.get("cache_creation_input_tokens") or 0) + (u.get("input_tokens") or 0)
        line = "  %02d  %6d tokens sent, %6d read from cache" % (n, sent, read)
        if previous:
            line += "  = %3d%% of the previous request reused" % round(100 * read / previous)
        lines += [line, "      request id %s   at %s" % (h.get("x-request-id", "none"), h.get("date", "?"))]
        previous = sent
        time.sleep(1)
    (out / "output.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
