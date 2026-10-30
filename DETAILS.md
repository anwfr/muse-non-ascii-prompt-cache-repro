# Details

Start with [`README.md`](README.md). Model `muse-spark-1.3-contributor`, endpoint
`https://api.meta.ai/v1/messages`, 2026-10-30, 09:11 to 09:23 UTC. A request is "read in full" when it
reads at least 97 % of the previous request from cache.

## Six cases

[`repro-nonascii.py`](repro-nonascii.py), run three times ([`runs/six-cases_1`](runs/six-cases_1/),
`_2`, `_3`). The same growing conversation of four requests; only the place and number of em dashes
change. Requests 2 to 4 of each run:

| case | requests | read in full |
|---|---|---|
| A. one tool, ASCII description | 9 | 9 |
| B. same tool, six em dashes in its description | 9 | 2 |
| C. same tool, one em dash in its description | 9 | 9 |
| D. no tool, six em dashes at character 100 of the system prompt | 9 | 4 |
| E. no tool, the same six em dashes at character 5 000 of the system prompt | 9 | 9 |
| F. case A without any `cache_control` marker | 9 | 6 |

So: one em dash is fine (C), six are not (B); the same six em dashes fail near the start of the
request (D) and not after character 5 000 (E).

## Pauses between requests

[`pause-probe.py`](pause-probe.py) `2 10 30` ([`runs/pauses`](runs/pauses/)): cases A and B with 2, 10
and 30 seconds between requests. Case B still misses with 10 and 30 seconds, so the misses are not a
delay in writing the cache.

## Partial reads

Every partial read (52 to 75 %) is, to the token, a full read of an older request of the same
conversation (request 1 or 2), never a cut inside the previous one.

## Inside each run folder

- `output.txt`: what the script printed.
- `requests/*.request.json`: the exact body sent.
- `requests/*.response.json`: the response body with its `x-request-id` and date (the six-case
  runs also keep the status and all response headers). The API key is never saved.
