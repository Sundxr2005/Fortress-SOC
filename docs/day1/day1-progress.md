# Day 1 — Foundation & Architecture

## Member: Jagan (Architecture Lead + SIEM Integration)

## Completed Tasks
- Deployed Wazuh Manager 4.7.0 via Docker on Mac M1
- Confirmed core services running: analysisd, remoted, authd, execd, apid
- Generated agent enrollment keys for all 3 team VMs
- Shared Wazuh Manager IP and keys with all teammates
- Locked JSON alert schema with Member 4 (SOAR)
- Architecture diagram finalized and uploaded

## Wazuh Manager Status
- Host: Mac M1 (Docker container)
- Ports: 1514 (agent logs), 1515 (enrollment), 55000 (API)
- Agents registered: suricata-vm (001), waf-vm (002), kali-vm (003)

## JSON Alert Schema (agreed with Member 4)
{
  "rule_id": "",
  "rule_level": "",
  "rule_description": "",
  "src_ip": "",
  "dst_ip": "",
  "agent_name": "",
  "timestamp": "",
  "full_log": ""
}

## Pending for Day 2
- Confirm agents connect and show Active status
- Verify Suricata alerts appear in Wazuh
- Build Wazuh → Shuffle integration script

updated by jagan928032
