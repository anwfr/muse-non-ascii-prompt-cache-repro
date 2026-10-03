"""Does each Claude Code request start exactly like the previous one? python3 check-prefix.py <run-dir>...

Compares consecutive conversation requests (those carrying tools): tools, system, then messages one by one,
cache_control markers removed. Prints the first place where request n+1 stops repeating request n.
"""
import copy, hashlib, json, pathlib, sys


def strip(node):
    if isinstance(node, dict):
        return {k: strip(v) for k, v in node.items() if k != "cache_control"}
    if isinstance(node, list):
        return [strip(v) for v in node]
    return node


def same_text(node):
    """A content given as one text block, or as the same plain string: the same text, made equal here."""
    if isinstance(node, dict):
        out = {k: same_text(v) for k, v in node.items()}
        c = out.get("content")
        if isinstance(c, list) and len(c) == 1 and isinstance(c[0], dict) and set(c[0]) == {"type", "text"}:
            out["content"] = c[0]["text"]
        return out
    if isinstance(node, list):
        return [same_text(v) for v in node]
    return node


def h(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]


def first_diff(a, b, path=""):
    """Path of the first difference between two JSON values, with a short view of both sides."""
    if type(a) != type(b):
        return path, repr(a)[:120], repr(b)[:120]
    if isinstance(a, dict):
        for k in list(a) + [k for k in b if k not in a]:
            if a.get(k) != b.get(k):
                return first_diff(a.get(k), b.get(k), "%s.%s" % (path, k))
        return None
    if isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return first_diff(x, y, "%s[%d]" % (path, i))
        if len(a) != len(b):
            return "%s (length %d vs %d)" % (path, len(a), len(b)), "", ""
        return None
    if a != b:
        sa, sb = str(a), str(b)
        i = next((k for k, (p, q) in enumerate(zip(sa, sb)) if p != q), min(len(sa), len(sb)))
        return "%s @char %d" % (path, i), sa[max(0, i - 60):i + 80], sb[max(0, i - 60):i + 80]
    return None


for run in sys.argv[1:]:
    reqs = []
    for f in sorted(pathlib.Path(run, "requests").glob("*.request.json")):
        body = json.loads(f.read_text())["body"]
        if body.get("tools"):
            reqs.append((f.name[:2], strip(body)))
    print("==", run, len(reqs), "conversation requests")
    for (na, a), (nb, b) in zip(reqs, reqs[1:]):
        problems = []
        if a.get("tools") != b.get("tools"):
            problems.append(("tools", first_diff(a.get("tools"), b.get("tools"), "tools")))
        if a.get("system") != b.get("system"):
            problems.append(("system", first_diff(a.get("system"), b.get("system"), "system")))
        ma, mb = a.get("messages", []), b.get("messages", [])
        for i, m in enumerate(ma):
            if i >= len(mb) or m != mb[i]:
                problems.append(("messages", first_diff(m, mb[i] if i < len(mb) else None, "messages[%d](%s)" % (i, m.get("role")))))
                break
        if not problems:
            print("  %s -> %s : request %s repeated exactly (%d messages kept, %d added)" % (na, nb, na, len(ma), len(mb) - len(ma)))
            continue
        na_, nb_ = same_text(a), same_text(b)
        if na_.get("tools") == nb_.get("tools") and na_.get("system") == nb_.get("system") \
                and na_.get("messages", []) == nb_.get("messages", [])[:len(ma)]:
            print("  %s -> %s : request %s repeated exactly once a one-block text and the same plain string count"
                  " as equal (%d messages kept, %d added)" % (na, nb, na, len(ma), len(mb) - len(ma)))
            continue
        for where, d in problems:
            print("  %s -> %s : DIFFERS in %s at %s" % (na, nb, where, d[0] if d else "?"))
            if d and d[1]:
                print("       before: %r" % d[1])
                print("       after : %r" % d[2])
