# Day 2 Progress — Jagan (Architecture Lead + Member 2 Coverage)

## Note: Member 2 (Suricata/Detection) was absent today.
## I covered their tasks in addition to my own.

## MY TASKS COMPLETED:

### 1. Suricata IDS Deployed (Member 2's task)
- Installed Suricata 7.0.3 on Ubuntu 24.04 VM (UTM)
- Configured AF-PACKET mode on enp0s1 interface
- Enabled EVE JSON output at /var/log/suricata/eve.json
- Updated Suricata rules via suricata-update
- Status: Active and running

### 2. Wazuh Agent Installed on Ubuntu VM
- Installed Wazuh Agent 4.7.0 (matching Manager version)
- Configured to point to Manager at 192.168.64.1:1514
- Configured localfile to read Suricata eve.json
- Status: Active and sending logs

### 3. Attack Simulations Run
- Nmap port scan: sudo nmap -sS 192.168.64.1
- Nmap version scan: sudo nmap -sV 192.168.64.1
- Hydra brute force: hydra -l admin -P wordlist.txt ssh://192.168.64.4
- All attacks generated Suricata alerts in eve.json

### 4. Wazuh Manager Running
- All core services running: analysisd, remoted, authd
- Receiving logs from Ubuntu agent
- alerts.log confirmed receiving real alerts

### 5. Wazuh Indexer Issue
- Indexer incompatible with M1 ARM architecture
- x86 OpenSearch image cannot run under Rosetta emulation
- Solution: Moving indexer to Ubuntu UTM VM (x86 emulation)

## EVIDENCE
- Suricata eve.json: active, writing alerts
- Wazuh alerts.log: confirmed agent connected and sending
- Nmap scan results: 6 open ports discovered on gateway

## PENDING
- Wazuh Indexer inside Ubuntu VM
- Wazuh Dashboard
- Connect Manager to Indexer

