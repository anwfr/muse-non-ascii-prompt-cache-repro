# Muse loses the prompt cache when a few non-ASCII characters appear near the start of a request

Model `muse-spark-1.3-contributor`, endpoint `https://api.meta.ai/v1/messages`. Last checked on 2026-10-30.

**In one sentence:** the same conversation is read back from cache when its tool description is
plain ASCII, and mostly is not when that description contains six em dashes (`—`, U+2014).
ASCII-only requests cache correctly.

## The minimal case

[`repro.py`](repro.py) sends one conversation as four growing requests, each repeating the previous
one and adding a user turn. One tool, a cache marker on the system prompt and on the last message.
Two cases, which differ only by the tool description:

- **A:** `Returns the current time. Use it - when asked - for the time. Notes - a - b - c - d.`
- **B:** `Returns the current time. Use it — when asked — for the time. Notes — a — b — c — d.`

Expected in both: requests 2, 3 and 4 read the previous request from cache (97 to 100 %, Muse
counts cache reads in blocks of 128 tokens).

Share of the previous request read from cache, 2026-10-30, 09:23 UTC
([`runs/2026-10-30/minimal`](runs/2026-10-30/minimal/)):

| | requests 2, 3, 4 | request ids |
|---|---|---|
| A, run 1 | 98 %, 98 %, 100 % | `a1920f60-f16f-431f-9c5b-50a7ef1a597d`, `8ae7398c-3590-4508-a88b-c81213af9787`, `730b2695-6f87-4fa6-ba10-9b33332eec01` |
| B, run 1 | **0 %**, 98 %, 100 % | `fe3c4891-0905-4d04-aa9a-38d83a3ed9aa`, `eab47b77-1229-44ff-8035-6af6389e45b1`, `76a7ae42-5342-4795-b8b7-c6179f2a7fe8` |
| A, run 2 | 98 %, 98 %, 100 % | `da4b175e-0fc9-4c7f-ac70-ef2e71b52e1c`, `1163dc1f-9011-450e-b6c5-94e0183170c1`, `72456a74-3e2d-425b-aa1d-b61c34fadf66` |
| B, run 2 | 98 %, **0 %**, **75 %** | `140b7b6e-dad9-47ef-9a92-3d7e6c29a79d`, `478c4b35-f79a-4db0-9742-9d2de420c687`, `62d33094-cdc8-46b2-aef9-e6ee61886d6e` |
| A, run 3 | **0 %**, 98 %, 100 % | `0d49e109-2ba9-48ec-b759-d46b2d559f50`, `3c0631d1-46b6-4ecc-9879-651c27a372f7`, `ce0e6295-d18b-43bb-828e-ffd0a838208c` |
| B, run 3 | **0 %**, 98 %, **52 %** | `556b10ae-b25d-4b81-9b26-6e370e580a08`, `c08be789-e419-4d1d-a865-31186c552fa6`, `2bf0d72d-488e-4edb-a821-2cf7e1086bd1` |

Over every request sent on 2026-10-30 (the minimal case, three runs of the six-case script, and a
probe with pauses between requests), a request read the previous one in full:

| tool description or system prompt | requests read in full | mean share read |
|---|---|---|
| ASCII (A), a single em dash (C), or six em dashes after character 5 000 (E) | **43 of 45** | 94 % |
| six em dashes in the first ~4 096 characters, in the tool (B) or the system prompt (D) | **14 of 36** | 57 % |

A partial read (52 %, 68 %, 75 %) is a full read of an *older* request of the same conversation: the
entry written by the previous request exists, but is not found. Pausing 10 or 30 seconds between
requests does not help ([`runs/2026-10-30/pauses`](runs/2026-10-30/pauses/)), so this is not a delay
in writing the cache.

## Why it matters

Claude Code's first tool definition has three em dashes in its first 900 characters. On 2026-10-03,
every Claude Code session on Muse read almost nothing back from cache; the same sessions, with only
those characters replaced by ASCII by a local relay, read 14 requests out of 14 in full. Details in
[`DETAILS.md`](DETAILS.md#claude-code).

## What changed since 2026-10-03

On 2026-10-03, case B read **0 %** on every request of three runs; it now reads in full about a third
of the time. A request without any `cache_control` marker never read from cache then; it now reads
in full 6 times out of 9. Something changed on the Muse side, but the non-ASCII case is still far
worse than the ASCII one. The 2026-10-03 measurements are in [`DETAILS.md`](DETAILS.md) and
[`runs/2026-10-03`](runs/2026-10-03/).

## What we ask

1. Is a cache or routing key for `/v1/messages` computed from the first ~4 096 characters of the
   request, and how does it handle multi-byte UTF-8 characters? On 2026-10-03, em dashes at character
   4 000 of the system prompt lost the cache, at character 4 400 they did not; one em dash is fine,
   two are not.
2. What changed in caching between 2026-10-03 and 2026-10-30?

## Reproduce

```
API_KEY=<Muse key> python3 repro.py             # the minimal case, A against B, three runs
API_KEY=<Muse key> python3 repro-nonascii.py    # six cases: tool, system prompt, position, no marker
API_KEY=<Muse key> python3 pause-probe.py 2 10 30   # A and B with pauses between requests
```

Python 3 only, about one cent per script. Each script saves the exact request bodies and the
responses, with their `x-request-id`, in `./requests/`.
