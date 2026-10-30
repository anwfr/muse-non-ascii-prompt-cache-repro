"""Cases A (ASCII tool) and B (six em dashes in the tool), four growing requests, with a fixed pause between requests.
Run: API_KEY=<Muse key> python3 pause-probe.py <pause seconds>..."""
import json, os, pathlib, sys, time, urllib.request, uuid
URL = "https://api.meta.ai/v1/messages"; MODEL = "muse-spark-1.3-contributor"; KEY = os.environ["API_KEY"]; DASH = "—"
LONG = " ".join("Line %d: the quick brown fox jumps over the lazy dog." % i for i in range(120))
OUT = pathlib.Path("requests"); OUT.mkdir(exist_ok=True)
CASES = [("A", "Returns the current time. Use it - when asked - for the time. Notes - a - b - c - d."),
         ("B", "Returns the current time. Use it %s when asked %s for the time. Notes %s a %s b %s c %s d." % ((DASH,) * 6))]
def body(desc, turn, run):
    msgs = []
    for i in range(1, turn + 1):
        msgs.append({"role": "user", "content": [{"type": "text", "text": "Question %d. %s" % (i, LONG)}]})
        if i < turn: msgs.append({"role": "assistant", "content": [{"type": "text", "text": "ok"}]})
    msgs[-1]["content"][-1]["cache_control"] = {"type": "ephemeral"}
    return {"model": MODEL, "max_tokens": 16, "tools": [{"name": "get_time", "description": desc, "input_schema": {"type": "object", "properties": {}}}],
            "system": [{"type": "text", "text": "Run %s. Answer ok. %s" % (run, LONG), "cache_control": {"type": "ephemeral"}}], "messages": msgs}
for pause in map(float, sys.argv[1:]):
    for name, desc in CASES:
        run = uuid.uuid4().hex[:8]; prev = None; reads = []
        for turn in range(1, 5):
            raw = json.dumps(body(desc, turn, run), ensure_ascii=False)
            stem = "pause%g-%s-turn%d" % (pause, name, turn); (OUT / (stem + ".request.json")).write_text(raw)
            req = urllib.request.Request(URL, raw.encode(), {"anthropic-version": "2023-06-01", "content-type": "application/json", "x-api-key": KEY})
            with urllib.request.urlopen(req, timeout=120) as r:
                a = json.load(r); rid, date = r.headers.get("x-request-id"), r.headers.get("Date")
            (OUT / (stem + ".response.json")).write_text(json.dumps({"request_id": rid, "date": date, "response_body": a}, indent=1))
            u = a["usage"]; read = u.get("cache_read_input_tokens", 0); total = read + u.get("cache_creation_input_tokens", 0) + u["input_tokens"]
            reads.append("%s %3d%% (%s)" % ("req%d" % turn, round(100 * read / prev) if prev else 0, rid)); prev = total
            if turn < 4: time.sleep(pause)
        print("pause %4gs  case %s: %s" % (pause, name, " | ".join(reads[1:])), flush=True)
