# Brownie Point 4 — "The Map That Only Shows Roads Already Walked"

## Riddle Decode
The riddle describes a detection system that only knows what it 
has already been taught. Every Suricata signature is a road someone 
already drove — a known attack pattern written into a rule. If an 
attacker takes a brand new approach, Suricata has no rule for it 
and stays completely silent.

The answer: anomaly-based detection — instead of asking "does this 
match a known bad pattern", ask "does this behavior look statistically 
normal for this protocol?"

## What We Built
Enabled Suricata's built-in anomaly detection engine on Ubuntu VM:
- Edited /etc/suricata/suricata.yaml
- Set anomaly: enabled: yes
- This shifts Suricata from purely signature-based to also flagging 
  protocol-level behavioral anomalies

## Proof It Works
- eve.json shows applayer.anomaly.count: 1 firing on real traffic
- fast.log shows SURICATA STREAM FIN2 FIN with wrong seq
- eve.json piped into Wazuh via ossec.conf — every anomaly = SIEM alert

## Why This Matters
A zero-day attack has no signature. Anomaly detection catches it 
because the attack still communicates over real protocols — and real 
protocols have expected behavior. The moment the attacker does 
something the protocol was never designed to do, the anomaly engine 
fires even without knowing what the attack is.

## Commands Used
sudo grep -A5 "anomaly" /etc/suricata/suricata.yaml
sudo cat /var/log/suricata/eve.json | grep anomaly | tail -3
sudo tail -10 /var/log/suricata/fast.log
sudo nmap -sS -p 1-1000 192.168.64.1
