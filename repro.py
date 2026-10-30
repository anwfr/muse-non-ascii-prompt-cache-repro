"""Minimal case: the same conversation with one tool, sent as four growing requests.
A: the tool description is ASCII. B: the same description with six em dashes (U+2014).
Expected in both: requests 2 to 4 read the previous request from cache (97 to 100 %).

Run:  API_KEY=<Muse key> python3 repro.py
Python 3 only, about 0.01 USD. Each request and response is saved in ./requests/
"""
import json, os, pathlib, time, urllib.request, uuid

URL = "https://api.meta.ai/v1/messages"
MODEL = "muse-spark-1.3-contributor"
KEY = os.environ["API_KEY"]
RUNS = 3
LONG = " ".join("Line %d: the quick brown fox jumps over the lazy dog." % i for i in range(120))
CASES = {
    "A (ASCII)": "Returns the current time. Use it - when asked - for the time. Notes - a - b - c - d.",
    "B (six em dashes)": "Returns the current time. Use it — when asked — for the time. Notes — a — b — c — d.",
}
OUT = pathlib.Path("requests")
OUT.mkdir(exist_ok=True)


def body(description, turn, tag):
    messages = []
    for i in range(1, turn + 1):
        messages.append({"role": "user", "content": [{"type": "text", "text": "Question %d. %s" % (i, LONG)}]})
        if i < turn:
            messages.append({"role": "assistant", "content": [{"type": "text", "text": "ok"}]})
    messages[-1]["content"][-1]["cache_control"] = {"type": "ephemeral"}
    return {"model": MODEL, "max_tokens": 16,
            "tools": [{"name": "get_time", "description": description, "input_schema": {"type": "object", "properties": {}}}],
            "system": [{"type": "text", "text": "Run %s. Answer ok. %s" % (tag, LONG), "cache_control": {"type": "ephemeral"}}],
            "messages": messages}


print("Model %s, %s\nShare of the previous request read from cache, requests 2, 3, 4:" % (MODEL, URL))
for run in range(1, RUNS + 1):
    for case, description in CASES.items():
        tag, previous, shares = uuid.uuid4().hex[:8], None, []  # new tag: nothing cached at the start
        for turn in range(1, 5):
            raw = json.dumps(body(description, turn, tag), ensure_ascii=False)
            stem = "run%d-%s-turn%d" % (run, case[0], turn)
            (OUT / (stem + ".request.json")).write_text(raw)
            request = urllib.request.Request(URL, raw.encode("utf-8"), {
                "anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": KEY})
            with urllib.request.urlopen(request, timeout=120) as r:
                answer, request_id, date = json.load(r), r.headers.get("x-request-id"), r.headers.get("Date")
            (OUT / (stem + ".response.json")).write_text(json.dumps(
                {"x-request-id": request_id, "date": date, "body": answer}, indent=1))
            usage = answer["usage"]
            read = usage.get("cache_read_input_tokens", 0)
            if previous:
                shares.append("%3d%% (%s)" % (round(100 * read / previous), request_id))
            previous = read + usage.get("cache_creation_input_tokens", 0) + usage["input_tokens"]
            time.sleep(1)
        print("run %d  %-18s %s" % (run, case, "  ".join(shares)), flush=True)
