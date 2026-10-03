# Details: every run, the threshold, the window, the workaround

Start with [`README.md`](README.md). This page is for the engineer who wants to check every claim
against a file.

## All runs

2026-10-03, model `muse-spark-1.3-contributor`, endpoint `https://api.meta.ai/v1/messages`, Claude Code
2.1.288. The last column is how much of the previous request each request read from cache; expected:
100 %. Muse counts cache reads in blocks of 128 tokens, so a full read of a small request shows as 97 to
99 %.

<!-- results -->
| run folder | where | what runs | what differs | setting | read back from the previous request, request 2 onwards |
|---|---|---|---|---|---|
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case A: one tool, ASCII description | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case A: one tool, ASCII description | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case A: one tool, ASCII description | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case B: same tool, six em dashes in its description | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case B: same tool, six em dashes in its description | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case B: same tool, six em dashes in its description | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case C: same tool, one em dash | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case C: same tool, one em dash | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case C: same tool, one em dash | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case D: no tool, six em dashes at character 100 of the system prompt | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case D: no tool, six em dashes at character 100 of the system prompt | — | 97 %, 0 %, 0 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case D: no tool, six em dashes at character 100 of the system prompt | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case E: no tool, six em dashes at character 5 000 of the system prompt | — | 97 %, 98 %, 100 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case E: no tool, six em dashes at character 5 000 of the system prompt | — | 97 %, 98 %, 0 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case E: no tool, six em dashes at character 5 000 of the system prompt | — | 98 %, 98 %, 100 % |
| [`nonascii_muse_1`](runs/nonascii_muse_1/) | Muse | Test script | case F: case A without any cache marker | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_2`](runs/nonascii_muse_2/) | Muse | Test script | case F: case A without any cache marker | — | 0 %, 0 %, 0 % |
| [`nonascii_muse_3`](runs/nonascii_muse_3/) | Muse | Test script | case F: case A without any cache marker | — | 0 %, 0 %, 0 % |
| [`claude-code_muse_1`](runs/claude-code_muse_1/) | Muse | Claude Code | default settings | — | 0 %, 0 %, 0 %, 0 % |
| [`claude-code_muse_2`](runs/claude-code_muse_2/) | Muse | Claude Code | default settings | — | 0 %, 0 %, 0 %, 0 % |
| [`claude-code_muse_3`](runs/claude-code_muse_3/) | Muse | Claude Code | default settings | — | 0 %, 0 %, 0 %, 0 %, 95 % |
| [`claude-code_muse_4`](runs/claude-code_muse_4/) | Muse | Claude Code | default settings | — | 0 %, 0 %, 0 %, 0 % |
| [`claude-code-asciitools_muse_1`](runs/claude-code-asciitools_muse_1/) | Muse | Claude Code | tool descriptions folded to ASCII by the relay | — | 99 %, 100 %, 100 %, 100 %, 100 % |
| [`claude-code-asciitools_muse_2`](runs/claude-code-asciitools_muse_2/) | Muse | Claude Code | tool descriptions folded to ASCII by the relay | — | 99 %, 100 %, 100 %, 100 %, 100 % |
| [`claude-code-asciitools_muse_3`](runs/claude-code-asciitools_muse_3/) | Muse | Claude Code | tool descriptions folded to ASCII by the relay | — | 99 %, 100 %, 100 %, 100 % |
| [`replay_muse_1_as-is`](runs/replay_muse_1_as-is/) | Muse | Replay of Claude Code | the recorded requests, as sent | — | 0 %, 0 %, 0 %, 0 % |
| [`replay_muse_2_as-is`](runs/replay_muse_2_as-is/) | Muse | Replay of Claude Code | the recorded requests, as sent | — | 0 %, 0 %, 0 %, 0 % |
| [`replay_muse_3_as-is`](runs/replay_muse_3_as-is/) | Muse | Replay of Claude Code | the recorded requests, as sent | — | 0 %, 0 %, 0 %, 70 %, 0 % |
| [`replay_muse_1_ascii-tools`](runs/replay_muse_1_ascii-tools/) | Muse | Replay of Claude Code | tool descriptions folded to ASCII | — | 0 %, 100 %, 100 %, 100 % |
| [`replay_muse_2_ascii-tools`](runs/replay_muse_2_ascii-tools/) | Muse | Replay of Claude Code | tool descriptions folded to ASCII | — | 99 %, 100 %, 100 %, 100 % |
| [`replay_muse_3_ascii-tools`](runs/replay_muse_3_ascii-tools/) | Muse | Replay of Claude Code | tool descriptions folded to ASCII | — | 99 %, 100 %, 100 %, 100 %, 100 % |
<!-- /results -->

## Threshold and window

Trials made with a growing synthetic conversation of three or four requests, like the test script, with
one element added at a time. Each line is one trial; the shares are those of requests 2 onwards. Every
request of every trial, with its `x-request-id` and time, is in [`probes.csv`](probes.csv) (2026-10-03,
15:55 to 16:32 UTC). Their bodies are not included: several use Claude Code's own tool text.

**Threshold: one em dash is fine, two are not.**

| trial | read from cache | first request id |
|---|---|---|
| one tool (Claude Code's `Write`, ASCII description) | 99 %, 98 %, 98 % (twice) | `aa4460eb-d90a-433d-a678-5d77e4cf54bc` |
| same, plus one em dash | 99 %, 98 %, 98 % | `e08788b6-f87b-487c-a994-989073d8b1a6` |
| same, plus one ellipsis `…`, or plus one arrow `→` | 99 %, 98 %, 98 % (each) | `a56033a6-8fe8-4899-a156-c7f621405ff7`, `9dfb8410-3f61-434a-850f-4f538f09dae3` |
| same, plus two em dashes | **0 %, 0 %, 0 %** (twice) | `96ea5e4f-e3e3-4c09-a1cb-bc525a54bbd6`, `23aaf971-1032-4e88-b508-a6ffd7f5fc65` |
| one hand-written tool, two em dashes | **0 %, 0 %, 0 %** (three times) | `7159a4eb-a3d0-4959-8246-9970e5d4245d`, `4cf2e606-fdf7-4263-8ad5-aa3522b0d8f2`, `f22f7b8d-10fe-4c23-9f54-9c9fbb68a294` |
| two tools (`Edit`, `WebFetch`), one em dash each | **0 %, 0 %, 0 %** | `8be9824a-b641-4641-8032-5b892796b2f6` |
| one tool (`Write`), plus two `é` / three `é` | 98 %, 98 %, 98 % / 98 %, 98 %, 100 % | `11bc0a0c-0c2f-4a51-9ac6-02b135807d15`, `5838d97a-54b1-402d-96c9-a5c3f8013ca9` |
| one tool (`Write`), plus four `é` | **0 %, 69 %, 0 %** | `46ef9b7d-28cf-4cc9-ba41-6accee9753fb` |
| one tool (`Write`), plus two `🤖` | **0 %, 0 %, 0 %** | `5da96dd1-ef8c-4f7d-a7cc-488659d01f1f` |

Two em dashes: 0 of 15 requests read. In UTF-8, `—` takes 3 bytes (2 more than its one character), `é`
2 bytes (1 more), `🤖` 4 bytes (3 more). On these small samples, the cache holds up to 3 extra bytes and
fails from 4 on. It looks like a length counted in characters in one place and in bytes in another; we
cannot check that from the outside.

**Window: only about the first 4 096 characters count, tool definitions first, then the system prompt,
then the messages.**

| trial | read from cache | first request id |
|---|---|---|
| no tool, six em dashes at character 3 000 of the system prompt | **0 %, 0 %, 49 %** | `15f26c00-9ab4-4169-8646-8684a781f0b5` |
| same at character 3 800, 4 000 | **0 %, 0 %, 0 %** (each) | `eb04b59b-7da7-440d-a216-895e2ac1087e`, `84fba7d8-6503-4ad5-b20f-c3ebebaae859` |
| same at character 4 150 | 0 %, 98 %, 100 % | `e3ca4545-37f1-41df-8813-16c60e6a0b4e` |
| same at character 4 400, 5 200 | 98 %, 98 %, 100 % (each) | `9f49731d-9383-4ff7-a09f-58fd6fd5e3fd`, `57bc7d49-a0eb-4909-b28f-08f586d82c1c` |
| one tool (`Write`, ASCII), five em dashes at the start of the system prompt | **0 %, 0 %, 0 %** | `9ff4a6a9-310d-4f1e-9472-caf7755b37bf` |
| one tool (`Write`, ASCII), twenty em dashes at the end of the system prompt (past character 6 600) | 99 %, 99 %, 99 % | `ddf5ccf7-ce2d-43d5-b1f8-a0b40360d9d3` |
| one-line system prompt, five em dashes at the start of the first message | **0 %, 0 %, 0 %** | `a924153a-ae8e-47f4-8e60-03bda37f3532` |
| the same without em dashes (control) | 97 %, 97 %, 0 % | `87c8d112-361b-4a24-9687-e58b4a4a0b00` |
| Claude Code's 21 tools, only the first (`Agent`, 3 243 characters) folded to ASCII | 100 %, 99 % | `bca48fad-606f-4d68-a339-453d6ce602ec` |
| Claude Code's 21 tools, all folded to ASCII except the first three | **0 %, 0 %** | `9803ce23-1c1c-4dbd-97df-fce1747f5350` |
| Claude Code's 21 tools folded to ASCII, one non-ASCII character left / two left | 100 %, 99 % / **0 %, 0 %** | `fd857f3e-7ec1-4533-b345-d09b41628968`, `28a85ad4-2c54-497e-a269-026a6ac3a4f8` |

The limit lies between character 4 000 and 4 150 of the system prompt when there is no tool: 4 096 is our
guess, not a value we can read. With only `Agent` folded, a single non-ASCII character is left before
character 4 096 (an em dash in `Bash`, at character 3 396 of the compact JSON of the tools): the cache
holds, as the threshold predicts.

**It is the decoded text that counts.** The same body sent as pure ASCII, with `\u2014` escapes instead of
`—`: 0 %, 0 %, 0 % (`1619f596-ecb9-4a82-b617-c76275f3c670`).

## Cache markers

Your prompt caching page says that no marker is needed. On `/v1/messages`, a request without any
`cache_control` marker is never read from cache, even in pure ASCII: case F of the test script, and the
trials below. One marker is enough, on the system prompt or on the last message.

| trial | read from cache | first request id |
|---|---|---|
| no tool, no marker | **0 %, 0 %, 0 %** | `96692ae3-8879-437c-b4b9-ec21780a6da4` |
| one tool (`Write`, ASCII), no marker | **0 %, 0 %, 0 %** | `737b1325-73c3-4a3e-a8a5-01858a4c7526` |
| no tool, one marker, on the system prompt only | 98 %, 98 %, 100 % | `89288322-fcd3-45ce-918e-23e2c57b2486` |
| no tool, one marker, on the last message only | 98 %, 98 %, 100 % | `b61c3d94-eb8d-4032-b45f-797c9d084443` |

`prompt_cache_key`, which the same page offers, is refused on `/v1/messages`:
`400 unknown parameter prompt_cache_key` (`9fea41a2-2ee3-49cb-94ad-ab6ccb0a39d5`,
[`runs/prompt-cache-key_muse_1`](runs/prompt-cache-key_muse_1/)).

## Claude Code

- **Its requests are append-only.** `check-prefix.py` on the seven Claude Code runs: from one
  conversation request to the next, the tool definitions, the system prompt and every earlier message are
  repeated exactly, then three messages are added. The only difference is the form of the last
  `role: "system"` note: a list with one text block (it carries the cache marker), then a plain string with
  the same text. `check-prefix.py` also counts the request Muse refused (see « Also seen »), hence a first
  line « 0 added ».
- **Its tool definitions carry 126 non-ASCII characters**: `—` 103 times, `→` 14 times, `–` 4 times, `…` 3
  times, `≤` and `×` once each. The first tool, `Agent`, has three em dashes in its first 900 characters.
  Its system prompt carries more em dashes.
- **A replay of the recorded requests, unchanged, gets the same 0 %**, apart from one partial read of an
  older request (`replay_muse_*_as-is`): it does not depend on how Claude Code calls the API.
- **The same replay with the tool descriptions folded to ASCII reads 12 requests out of 13 in full**
  (`replay_muse_*_ascii-tools`).
  Only the `description` strings change (`—` becomes `-`, `→` becomes `->`, see
  [`ascii_tools.py`](ascii_tools.py)); names, types, enums and schemas are unchanged.
- **When a request misses, it sometimes reads an older request in full.** In `claude-code_muse_3`, request
  11 reads 35 953 tokens, the size of request 07 (35 989), not of request 10. In `probes.csv`, trial « four
  `é` », request 3 reads 3 953 tokens, the size of request 1 (4 028). The cache entry exists, non-ASCII
  characters included; it looks like it is there but not found.

## Workaround

On our side, the tool descriptions folded to ASCII restore the cache: names, types, enums and schemas
are unchanged, so the model still gets complete tools ([`ascii_tools.py`](ascii_tools.py)). The
recording relay applies it with `claude-code-compare.py muse <out-dir> --ascii-tools`.

- **Three real Claude Code 2.1.288 sessions with the relay option**, 2026-10-03, 17:05 to 17:07 UTC: 14
  conversation requests out of 14 read 99 or 100 % of the previous one; the task was completed (answer
  « ok ») each time; no non-ASCII character was left in `tools`
  (`claude-code-asciitools_muse_1` to `_3`, first conversation requests `8d5282d6-f6fe-44d2-be71-edfb75a9a976`,
  `84831381-758f-42f3-b04c-cd935d14ae40`, `aac7da69-5fe7-4bfe-9b2e-c1b34810f225`).
- **Control session, same relay without the option**, right after (17:07 UTC): 0 of 4
  (`claude-code_muse_4`, first conversation request `3aa7dc86-cf82-46e3-b137-0843e81d6fef`).
- **Replays with the tool descriptions folded** (`replay_muse_*_ascii-tools`, 17:09 to 17:12 UTC): 12
  requests out of 13 read in full. The miss is request 2 of the first replay
  (`5c07b4c0-4b13-4709-ba80-e2d23f8d4614`); healthy requests miss now and then too (test script, run 2,
  case E, request 4).

This workaround holds only while the tool definitions fill about the first 4 096 characters: with fewer tools,
the window reaches Claude Code's system prompt, which carries eleven em dashes. We have not tried that
case.

## History

[`history.csv`](history.csv): our own Claude Code sessions on Muse, read from our local session logs
(one line per day, median share of the previous request read from cache). 97.7 to 99.5 % each day from
2026-09-20 to 09-27 (Claude Code 2.1.278 to 2.1.283), 85.7 % on 09-28 (2.1.283, 66 sessions), 0 % on
10-03 (2.1.288, 17 sessions); no session on Muse from 09-29 to 10-02. We have not checked whether the tool
definitions of Claude Code 2.1.283 already carried these em dashes.

## Also seen

- On its first request, Claude Code sends Muse a `safeguards` field, which Muse refuses
  (`400 unknown parameter safeguards`); Claude Code sends the request again without it. Unrelated to the
  cache: the replays never send it.
- Claude Code's permission check sends a side request with `stop_sequences`, which Muse refuses
  (`400 stop_sequences is not supported`, `claude-code-asciitools_muse_1`, request 09). Unrelated to the
  cache.
- Muse refuses `max_tokens` below 16; the test script uses 16.

## Inside each run folder

- `output.txt`: one line per request, with tokens sent, tokens read from cache, the request id
  (`x-request-id`) and the time.
- `requests/`: one pair of files per request, in order.
  - `….request.json`: the body sent.
  - `….response.json`: URL, request headers (key hidden), status, response headers (`x-request-id`,
    `x-route`, `Date`), and the response.
- `run.json` (Claude Code runs): model, Claude Code version, relay option, Claude Code's answer.

In the Claude Code runs, a few values are hidden in the saved bodies, listed in each file's `redacted`
field: device and session ids, an email address, the home directory path, and the text of personal
instruction files. The recorded Claude Code sessions (`runs/claude-code_*`) and their replays
(`runs/replay_*`) carry Claude Code's own prompt text: they are not in this public repository; we can
share them privately on request.

## Reproduce

```
API_KEY=<Muse key> python3 repro-nonascii.py                                     # the six cases
API_KEY=<Muse key> python3 replay.py runs/claude-code_muse_1 out-a as-is         # Claude Code requests: 0 %
API_KEY=<Muse key> python3 replay.py runs/claude-code_muse_1 out-b ascii-tools   # same, tool descriptions in ASCII: read in full
python3 check-prefix.py runs/claude-code*
MUSE_API_KEY=<Muse key> python3 claude-code-compare.py muse out-c                # a new Claude Code session, recorded
MUSE_API_KEY=<Muse key> python3 claude-code-compare.py muse out-d --ascii-tools  # the same, with the workaround
```
