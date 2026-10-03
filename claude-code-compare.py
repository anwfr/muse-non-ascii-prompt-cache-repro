"""A small Claude Code task run on Muse, every exchange recorded.

Claude Code reads four files, one per request (each file names the next one),
so the conversation grows. A local relay between Claude Code and Muse
records every exchange as it passes.

Run:
  MUSE_API_KEY=<Muse key> python3 claude-code-compare.py muse <out-dir>
  MUSE_API_KEY=<Muse key> python3 claude-code-compare.py muse <out-dir> --ascii-tools
      --ascii-tools: the relay folds the tool descriptions to ASCII before forwarding (the workaround, see
      ascii_tools.py); nothing else in the request changes
  python3 claude-code-compare.py --report <out-dir>           # rebuild output.txt from the saved traffic
Needs Python 3 and the `claude` command. Writes into <out-dir>:
  output.txt                 one line per request: tokens, cache read, request id, message id
  run.json                   model, Claude Code version, relay option, Claude Code's answer
  requests/NN.request.json   the body sent to Muse (redactions listed in "redacted")
  requests/NN.response.json  URL, request headers (key hidden), status, response headers, raw response
"""
import http.client, json, os, pathlib, re, subprocess, sys, tempfile, threading, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from ascii_tools import fold_descriptions

MODEL = "muse-spark-1.3-contributor"
UPSTREAM = "api.meta.ai"
TASK = ("Read start.txt with the Read tool. Its last line names the next file to read. "
        "Keep reading file after file until a file ends with END, then answer with the single word ok.")
SECRET_HEADERS = {"authorization", "x-api-key", "cookie", "set-cookie", "x-claude-code-session-id"}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
HOP = {"host", "content-length", "connection", "transfer-encoding", "accept-encoding", "keep-alive"}
# Personal text that Claude Code copies into its prompt (your own instruction files) is
# replaced by its length in the saved copies; nothing else is changed.
PERSONAL = [t.strip() for t in (p.read_text() for p in (pathlib.Path.home() / ".claude").glob("*.md")) if t.strip()]
HOME = str(pathlib.Path.home())  # the home directory path becomes "~"
CLAUDE_MD = re.compile(r"<user_claude_md>.*?</user_claude_md>", re.S)
OPTIONS = ("--ascii-tools",)


def redact(node, found):
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k == "metadata":
                out[k] = "<redacted: device and session ids>"
                found.add("metadata")
            else:
                out[k] = redact(v, found)
        return out
    if isinstance(node, list):
        return [redact(v, found) for v in node]
    if isinstance(node, str):
        if EMAIL.search(node):
            node = EMAIL.sub("<redacted: email>", node)
            found.add("email address")
        for text in PERSONAL:
            if text in node:
                node = node.replace(text, "<redacted: personal instruction file, %d chars>" % len(text))
                found.add("personal instruction files")
        if CLAUDE_MD.search(node):  # the safety check quotes them indented, so the exact match above misses them
            node = CLAUDE_MD.sub(lambda m: "<user_claude_md><redacted: personal instruction files, %d chars></user_claude_md>"
                                 % len(m.group(0)), node)
            found.add("personal instruction files")
        if HOME in node:
            node = node.replace(HOME, "~")
            found.add("home directory path")
    return node


def ascii_tools(raw):
    """The workaround, applied by the relay: tool descriptions folded to ASCII, the rest unchanged."""
    try:
        body = json.loads(raw)
    except ValueError:
        return raw
    if not body.get("tools"):
        return raw
    body["tools"] = fold_descriptions(body["tools"])
    return json.dumps(body, ensure_ascii=False).encode("utf-8")


def record(out_dir, options=()):
    """Run Claude Code through the relay; save every exchange under out_dir/requests/."""
    transform = "--ascii-tools" in options
    exchanges = []

    class Relay(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            raw = self.rfile.read(int(self.headers.get("content-length") or 0))
            if transform and self.path.split("?")[0].endswith("/v1/messages"):
                raw = ascii_tools(raw)
            headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
            conn = http.client.HTTPSConnection(UPSTREAM, timeout=600)
            conn.request(self.command, self.path, body=raw or None,
                         headers=dict(headers, **{"accept-encoding": "identity"}))
            resp = conn.getresponse()
            self.send_response(resp.status)
            for k, v in resp.getheaders():
                if k.lower() not in HOP:
                    self.send_header(k, v)
            self.end_headers()
            chunks = []
            while True:
                chunk = resp.read1(65536)
                if not chunk:
                    break
                chunks.append(chunk)
                self.wfile.write(chunk)
                self.wfile.flush()
            conn.close()
            hide = lambda items: {k: ("<redacted>" if k.lower() in SECRET_HEADERS else v) for k, v in items}
            exchanges.append({"path": self.path, "raw": raw, "request_headers": hide(headers.items()),
                              "status": resp.status, "response_headers": hide(resp.getheaders()),
                              "response_raw": b"".join(chunks).decode("utf-8", "replace")})

        do_GET = do_POST

    server = ThreadingHTTPServer(("127.0.0.1", 0), Relay)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env = {k: v for k, v in os.environ.items() if not k.startswith("ANTHROPIC_")}
    # every request, side requests included, goes to the Muse model
    settings = {"apiKeyHelper": "printenv MUSE_API_KEY",
                "env": {"ANTHROPIC_BASE_URL": "http://127.0.0.1:%d" % server.server_address[1],
                        "ANTHROPIC_SMALL_FAST_MODEL": MODEL, "ANTHROPIC_DEFAULT_OPUS_MODEL": MODEL,
                        "ANTHROPIC_DEFAULT_SONNET_MODEL": MODEL, "ANTHROPIC_DEFAULT_HAIKU_MODEL": MODEL,
                        "CLAUDE_CODE_SUBAGENT_MODEL": MODEL, "DISABLE_TELEMETRY": "1", "DISABLE_AUTOUPDATER": "1"}}
    with tempfile.TemporaryDirectory() as work:
        names = ["start"] + [uuid.uuid4().hex[:8] for _ in range(3)] + ["END"]
        for name, following in zip(names, names[1:]):  # four files of about 6 000 tokens each
            lines = ["%s line %d: the quick brown fox jumps over the lazy dog." % (name, i) for i in range(500)]
            last = "END" if following == "END" else "Next file: %s.txt" % following
            pathlib.Path(work, name + ".txt").write_text("\n".join(lines + [last]))
        pathlib.Path(work, "settings.json").write_text(json.dumps(settings))
        claude = subprocess.run(["claude", "-p", TASK, "--model", MODEL, "--allowedTools", "Read",
                                 "--strict-mcp-config", "--settings", "settings.json"],
                                cwd=work, env=env, capture_output=True, text=True, timeout=900)
    server.shutdown()
    (out_dir / "requests").mkdir(parents=True, exist_ok=True)
    for n, x in enumerate(exchanges, 1):
        found = set()
        body = redact(json.loads(x["raw"] or b"{}"), found)
        (out_dir / "requests" / ("%02d.request.json" % n)).write_text(
            json.dumps({"redacted": sorted(found), "body": body}, indent=1, ensure_ascii=False))
        (out_dir / "requests" / ("%02d.response.json" % n)).write_text(json.dumps(
            {"url": "https://%s%s" % (UPSTREAM, x["path"]), "request_headers": x["request_headers"],
             "status": x["status"], "response_headers": x["response_headers"], "response_raw": x["response_raw"]},
            indent=1, ensure_ascii=False))
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    (out_dir / "run.json").write_text(json.dumps(
        {"provider": "muse", "model": MODEL, "claude_code": version, "relay": [o for o in options if o in OPTIONS],
         "claude_answer": (claude.stdout or "")[-500:], "claude_exit": claude.returncode,
         "claude_error": (claude.stderr or "")[-500:] if claude.returncode else ""}, indent=1))


def usage_and_id(stream):
    """Usage (message_start updated by message_delta) and message id, from the raw response."""
    usage, message_id = {}, None
    for line in stream.splitlines():
        if line.startswith("data:"):
            try:
                event = json.loads(line[5:])
            except ValueError:
                continue
            if event.get("type") == "message_start":
                message_id = (event.get("message") or {}).get("id")
                usage.update((event.get("message") or {}).get("usage") or {})
            elif event.get("type") == "message_delta":
                usage.update({k: v for k, v in (event.get("usage") or {}).items() if v is not None})
    return usage, message_id


def report(out_dir):
    run = json.loads((out_dir / "run.json").read_text())
    lines = ["Claude Code %s on Muse, model %s%s" % (run["claude_code"], run["model"],
                                                   "".join(", relay %s" % o for o in run.get("relay", []))), "",
             "Conversation requests (they carry the tools). Expected from the second one on: 100% reused.", ""]
    side, previous = [], None
    for f in sorted((out_dir / "requests").glob("*.request.json")):
        n = f.name.split(".")[0]
        body = json.loads(f.read_text())["body"]
        response = json.loads((out_dir / "requests" / (n + ".response.json")).read_text())
        h = {k.lower(): v for k, v in response["response_headers"].items()}
        request_id = h.get("x-request-id") or "none"
        endpoint = response["url"].split("/v1/")[-1].split("?")[0]
        if not body.get("tools") or endpoint != "messages":
            side.append("  %s  %s, status %s, request id %s" % (n, endpoint, response["status"], request_id))
            continue
        if response["status"] != 200:
            lines += ["  %s  refused, HTTP %s: %s" % (n, response["status"], response["response_raw"][:160]),
                      "      request id %s   at %s" % (request_id, h.get("date", "?"))]
            continue
        u, message_id = usage_and_id(response["response_raw"])
        read = u.get("cache_read_input_tokens") or 0
        sent = read + (u.get("cache_creation_input_tokens") or 0) + (u.get("input_tokens") or 0)
        line = "  %s  %6d tokens sent, %6d read from cache" % (n, sent, read)
        if previous:
            line += "  = %3d%% of the previous request reused" % round(100 * read / previous)
        lines += [line, "      request id %s   message id %s   at %s" % (request_id, message_id, h.get("date", "?"))]
        previous = sent
    lines += ["", "Side requests (not part of the conversation):"] + (side or ["  none"])
    if run.get("claude_exit"):
        lines += ["", "claude exited with %s: %s" % (run["claude_exit"], run["claude_error"])]
    (out_dir / "output.txt").write_text("\n".join(lines) + "\n")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--report":
        print(report(pathlib.Path(sys.argv[2])))
    elif len(sys.argv) >= 3 and sys.argv[1] == "muse" and all(o in OPTIONS for o in sys.argv[3:]):
        record(pathlib.Path(sys.argv[2]), options=sys.argv[3:])
        print(report(pathlib.Path(sys.argv[2])))
    else:
        sys.exit("usage: python3 claude-code-compare.py muse <out-dir> [--ascii-tools]\n"
                 "       python3 claude-code-compare.py --report <out-dir>")
