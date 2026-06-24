# Day 4 — Final Demo Summary

## Team Present
- Jagan P V (Member 1) — Architecture Lead + SIEM
- N.S.H. Karthikeya (Member 3) — IAM + WAF

## What We Delivered

### All 4 Layers Working:
- Perimeter & Detection: Suricata IDS ✅
- SIEM & Visibility: Wazuh + Dashboard (300 hits) ✅
- Identity & Access: Keycloak RBAC (2 roles) ✅
- WAF & Response: ModSecurity (147/147 SQLi blocked) ✅

### Attacks Demonstrated:
- Nmap port scan ✅
- SQLMap SQL injection (blocked by WAF) ✅
- Hydra SSH brute force ✅

### Brownie Points:
- Day 1: Sleepwalker's Diary (correlation rules) ✅
- Day 2: Loyal Guard (Keycloak anomaly detection) ✅

### Connected Agents in Wazuh:
- suricata-vm (003) ✅
- member3-kali (007) ✅

### Live Pipeline:
Attack → WAF blocks → Wazuh alert → Dashboard shows → 300 alerts indexed

## Network
- Jagan Mac: 10.54.168.10
- Karthikeya Kali: 10.54.168.221
- Connected via hotspot

## GitHub
https://github.com/Sundxr2005/Fortress-SOC
