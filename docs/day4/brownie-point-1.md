# Brownie Point 1 — The Sleepwalker's Diary

## Riddle Decode
The riddle describes a stateless logging system that records 
events in isolation — no memory between entries, no pattern 
detection across time. A real attacker would exploit this by 
spreading their attack thinly over many sessions so no single 
log entry looks suspicious.

## Implementation
Time-windowed correlation rules in Wazuh local_rules.xml:

Rule 100001 (level 3): Single SSH failure → low severity log
Rule 100002 (level 12): 5 failures from same IP in 2 minutes 
→ correlated brute-force alert

This demonstrates the difference between:
- Stateless: 60 individual level-3 alerts (easy to ignore)
- Stateful: 1 level-12 correlated alert (impossible to miss)

## Evidence
- local_rules.xml: correlation rules deployed
- auth.log: 60 real SSH failures from Hydra attack
- Suricata eve.json: network-level detection of brute force

## Why This Matters
An attacker who knows your system is stateless will spread 
their attack over days. Our correlated rules catch this pattern 
even when individual events look innocent.

