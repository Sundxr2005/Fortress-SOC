# Member 3 (IAM + WAF) — Day 2 Progress Update

**Author:** N.S.H. Karthikeya
**Date:** June 23, 2026
**Status:** Core IAM + WAF objectives complete and verified. Currently blocked on SIEM integration pending Wazuh stack availability.

---

## Summary

Today's work focused on getting the entire IAM + WAF stack actually running and verified end-to-end in a fresh Kali Linux environment, after the original Windows setup failed to run at all (Docker Desktop installation error). All core Day 1/Day 2 deliverables for this role are now complete, including one full Brownie Point implementation. The remaining task — shipping WAF and Keycloak logs into Wazuh — is blocked pending the SIEM stack coming online.

---

## What Was Done Today

### 1. Migrated Full Stack to Kali Linux
The original Windows setup never executed — Docker Desktop failed to install due to a permissions error (`C:\ProgramData\DockerDesktop must be owned by an elevated account`). Rather than debug Windows-specific Docker issues mid-hackathon, the entire IAM/WAF stack was rebuilt and verified fresh inside a Kali VM, which is also a better long-term fit given the team's attack-simulation tooling needs.

### 2. Fixed Critical Network Isolation Bug
Discovered that this project's `docker-compose.yml` (IAM/WAF) and the SIEM team's `wazuh/docker-compose.yml` were each creating their own isolated Docker network by default. This meant Wazuh would never have been able to reach WAF or Keycloak logs, even once both stacks were running — a silent failure that would have blocked all cross-layer log shipping without an obvious error message.

**Fix applied:** created one shared external Docker network (`sentrix-net`, subnet `192.168.50.0/24`), updated both compose files to reference it as `external: true`, and assigned static IPs to every container across both stacks:

| IP | Service | Owner |
|---|---|---|
| `.10` / `.11` / `.12` | Wazuh Manager / Indexer / Dashboard | Jagan |
| `.21` | DVWA | Shared |
| `.40` | WAF (ModSecurity + Nginx) | Member 3 |
| `.50` | Keycloak | Member 3 |
| `.60` | Protected Flask app | Member 3 |

### 3. Fixed WAF Port Mapping Bug
The `owasp/modsecurity-crs:nginx` image listens internally on port **8080**, not port 80 as initially assumed. This caused all external requests to the WAF to reset with no response. Fixed by correcting the compose port mapping from `"80:80"` to `"80:8080"`. Confirmed fix by successfully receiving a proper HTTP 302 redirect from DVWA through the WAF.

### 4. Rebuilt and Verified Keycloak RBAC End-to-End
The Windows Keycloak setup never persisted (since Docker never actually ran there), so the realm, roles, client, and users were rebuilt from scratch in the working `Fortress-SOC` realm:
- Created roles: `admin`, `analyst`
- Created OIDC client: `sentrix-app`, wired to a custom protected Flask application
- Created two test users (`admin_1`, `analyst_1`) with distinct role assignments
- **Verified live:** both users successfully authenticate via Keycloak, and the protected Flask app correctly displays each user's distinct role — proving the RBAC chain works fully, not just in configuration.

### 5. Confirmed WAF Actively Blocks Real SQL Injection Attempts
Sent a live SQL injection payload (`' OR '1'='1`) through the WAF to DVWA. ModSecurity correctly:
- Detected the injection via OWASP CRS rule `942100` (libinjection SQLi detection)
- Escalated the request's inbound anomaly score past the configured threshold (rule `949110`)
- Blocked the request with HTTP `403 Forbidden`
- Logged the full event in structured JSON to the container's audit log (captured and committed as proof: `iam-waf/proof-screenshots/waf_sqli_block_proof.log`)

### 6. Implemented and Proved Brownie Point #2 — "The Loyal Guard Who Lets Everyone In"
**Decode:** The riddle describes authentication succeeding as a binary identity check while no one ever questions the *pattern* surrounding repeated logins — same user, multiple times, no behavioral context. Authentication confirms identity; it does not confirm intent.

**Build:** A Python service polling Keycloak's Admin REST API for login events every 10 seconds, flagging two anomaly conditions as a distinct elevated alert, separate from normal login events:
- Off-hours login (00:00–05:00)
- 3+ logins by the same user within a 5-minute window

**Proof:** Triggered 3 rapid logins as `admin_1`. The detector correctly escalated this into a `HIGH`-severity anomaly alert, distinct from the routine `INFO`-level events preceding it. Full decode notes and live output captured in `iam-waf/BROWNIE_POINT_2_COMPLETE.md`.

---

## Problems Faced and How They Were Solved

| Problem | Solution |
|---|---|
| Docker Desktop installation failed on Windows (permissions error) | Migrated entire stack to Kali Linux VM |
| Two separate Docker networks isolated IAM/WAF stack from SIEM stack | Created shared external `sentrix-net` network with static IPs across both compose files |
| YAML duplicate `networks:` key error | Identified and removed duplicate top-level key, validated with `docker compose config` before every run |
| WAF returned "connection reset" on all requests | Diagnosed via layered testing (internal container curl, port binding check, log inspection) — found the image listens on 8080 internally, fixed port mapping |
| GitHub rejected password authentication | Switched to Personal Access Token over HTTPS after SSH (port 22 and port 443 fallback) was blocked by the network |
| ModSecurity audit log file not found at expected path | Found via container filesystem search that this image logs to `/dev/stdout` instead of a file — now read via `docker logs waf` |
| `.gitignore`'s `*.log` rule silently blocked committing proof log | Added a targeted exception rule (`!iam-waf/proof-screenshots/*.log`) to allow evidence files through |

---

## Current Blocker

Attempted to reach the Wazuh manager (`192.168.50.10:55000`) and dashboard (`192.168.50.12:443`) to begin shipping WAF and Keycloak logs into the SIEM — both connections failed, indicating the Wazuh stack is not yet running.

**This blocks the remaining Day 2 core task** (log integration into SIEM as distinct, identifiable sources) and the Day 3 cross-layer proof requirement.

**Status:** Waiting on Jagan to confirm Wazuh Manager/Indexer/Dashboard are up and reachable on the shared network before proceeding with agent installation and log forwarding.

---

## Next Steps (Once Unblocked)

1. Install Wazuh agent on the WAF/Keycloak host, pointed at the manager
2. Configure log forwarding for WAF (`docker logs -f waf`) and Keycloak login events
3. Confirm both appear in the Wazuh dashboard as distinct sources from Suricata
4. Re-run the SQLi test and confirm the block is visible in the SIEM (Day 3's primary proof requirement)
