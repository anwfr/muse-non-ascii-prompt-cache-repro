"""Muse prompt cache: a few non-ASCII characters near the start of a request are enough to lose it.

Run:  API_KEY=<Muse key> python3 repro-nonascii.py
Needs Python 3 only. Costs about 0.01 USD. Saves every request (exact body) and response
(status, headers, body) in ./requests/

Six cases, the same growing conversation of four requests each. In cases A to E only the
place and number of em dashes (U+2014, 3 bytes in UTF-8) change; every request carries a
cache marker (`cache_control`) on the system prompt and on the last message, as Claude Code
does. Case F is case A without any cache marker. Expected everywhere: requests 2 to 4 read
the previous request from cache.
"""
import json, os, pathlib, sys, time, urllib.error, urllib.request, uuid

URL = "https://api.meta.ai/v1/messages"
MODEL = "muse-spark-1.3-contributor"
TURNS = 4
KEY = os.environ["API_KEY"]
DASH = "—"
LONG = " ".join("Line %d: the quick brown fox jumps over the lazy dog." % i for i in range(120))  # 6 600 characters
OUT = pathlib.Path("requests")
OUT.mkdir(exist_ok=True)


def tool(description):
    return [{"name": "get_time", "description": description, "input_schema": {"type": "object", "properties": {}}}]


def system_with_dashes(at):
    """The system prompt, with six em dashes inserted at character `at`."""
    return LONG[:at] + " %s a %s b %s c %s d %s e %s f " % ((DASH,) * 6) + LONG[at:]


# name, title, tools, system text (after the run tag), cache markers
CASES = [
    ("A-tool-ascii", "A - one tool, ASCII description", tool("Returns the current time. Use it - when asked - for the time. Notes - a - b - c - d."), LONG, True),
    ("B-tool-six-dashes", "B - same tool, six em dashes in its description", tool("Returns the current time. Use it %s when asked %s for the time. Notes %s a %s b %s c %s d." % ((DASH,) * 6)), LONG, True),
    ("C-tool-one-dash", "C - same tool, one em dash in its description", tool("Returns the current time. Use it %s when asked - for the time. Notes - a - b - c - d." % DASH), LONG, True),
    ("D-system-dashes-at-100", "D - no tool, six em dashes at character 100 of the system prompt", None, system_with_dashes(100), True),
    ("E-system-dashes-at-5000", "E - no tool, the same six em dashes at character 5 000 of the system prompt", None, system_with_dashes(5000), True),
    ("F-ascii-no-marker", "F - case A, without any cache marker", tool("Returns the current time. Use it - when asked - for the time. Notes - a - b - c - d."), LONG, False),
]


def request(tools, system, turn, run, markers):
    messages = []
    for i in range(1, turn + 1):
        messages.append({"role": "user", "content": [{"type": "text", "text": "Question %d. %s" % (i, LONG)}]})
        if i < turn:
            messages.append({"role": "assistant", "content": [{"type": "text", "text": "ok"}]})
    body = {"model": MODEL, "max_tokens": 16,  # Muse refuses fewer than 16
            "system": [{"type": "text", "text": "Run %s. Answer ok. %s" % (run, system)}], "messages": messages}
    if markers:
        body["system"][-1]["cache_control"] = {"type": "ephemeral"}
        messages[-1]["content"][-1]["cache_control"] = {"type": "ephemeral"}
    if tools:
        body["tools"] = tools
    return body


print("Model %s, %s" % (MODEL, URL))
for name, title, tools, system, markers in CASES:
    run = uuid.uuid4().hex[:8]  # new text each run, so nothing is cached at the start
    print("\n" + title)
    previous = None
    for turn in range(1, TURNS + 1):
        body = request(tools, system, turn, run, markers)
        raw = json.dumps(body, ensure_ascii=False)
        stem = "%s-turn%d" % (name, turn)
        (OUT / (stem + ".request.json")).write_text(raw)
        headers = {"anthropic-version": "2023-06-01", "content-type": "application/json"}
        req = urllib.request.Request(URL, raw.encode("utf-8"), dict(headers, **{"x-api-key": KEY}))
        exchange = {"url": URL, "request_headers": dict(headers, **{"x-api-key": "<redacted>"}), "request_body_file": stem + ".request.json"}
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                answer = json.load(r)
                exchange.update(status=r.status, response_headers=dict(r.headers.items()), response_body=answer)
                request_id, date = r.headers.get("x-request-id"), r.headers.get("Date")
        except urllib.error.HTTPError as e:
            error = e.read().decode("utf-8", "replace")
            exchange.update(status=e.code, response_headers=dict(e.headers.items()), response_body=error)
            (OUT / (stem + ".response.json")).write_text(json.dumps(exchange, indent=1))
            print("  request %d: refused, HTTP %d: %s" % (turn, e.code, error[:300]))
            break
        (OUT / (stem + ".response.json")).write_text(json.dumps(exchange, indent=1))
        u = answer["usage"]
        read = u.get("cache_read_input_tokens", 0)
        total = read + u.get("cache_creation_input_tokens", 0) + u["input_tokens"]
        line = "  request %d: %6d tokens sent, %6d read from cache" % (turn, total, read)
        if previous:
            line += "  = %3d%% of the previous request" % round(100 * read / previous)
        print(line + "   request id %s   %s" % (request_id, date))
        previous = total
        time.sleep(1)
    print("  expected on requests 2 to %d: 100%%" % TURNS)
