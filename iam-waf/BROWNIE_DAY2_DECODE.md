# Day 2 Brownie Point — "The Loyal Guard Who Lets Everyone In"

## Our Decode
The riddle describes authentication succeeding as a binary check (face matches
list, door opens) while no one ever asks about the *pattern* surrounding
repeated authentications — same user, multiple times, odd hours, no behavioral
context. Authentication alone confirms identity; it does not confirm intent
or safety.

## What We Built
A Python service polling Keycloak's Admin REST API for login events every 10
seconds. It maintains a rolling window of recent logins per user and flags two
anomaly conditions distinct from a normal login event:
1. Off-hours login (00:00–05:00)
2. 3+ logins by the same user within a 5-minute window

Both conditions write a HIGH-severity alert to a dedicated log file, separate
from normal INFO-level login events — directly modeling the riddle's ask:
distinguishing a login *event* from a login *pattern*.

## Why This Matters
A real attacker who has stolen valid credentials still authenticates
successfully every time — the credential check alone will never catch them.
Pattern-based analysis on top of authentication is what catches behavioral
anomalies that identity verification cannot.
