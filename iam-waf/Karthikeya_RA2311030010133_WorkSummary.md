# Member 3 — IAM + WAF Engineer: Complete Work Summary

**Name:** N.S.H. Karthikeya
**Register Number:** RA2311030010133
**Role:** Identity & Access Management (Keycloak) + Web Application Firewall (ModSecurity + Nginx)
**Last Updated:** June 23, 2026

---

## 1. Overview

This document summarizes all work completed for the IAM and WAF layers of the Mini Sentrix SOC project, covering environment setup, architecture decisions, problems encountered and resolved, attack simulations performed, and brownie point implementation.

---

## 2. Environment Migration: Windows → Kali Linux

Initial setup was attempted on Windows. Docker Desktop installation failed with a permissions error (`C:\ProgramData\DockerDesktop must be owned by an elevated account`), meaning no part of the stack had ever actually executed — only configuration files had been written. The entire stack was rebuilt and verified fresh inside a Kali Linux VM, which also better aligns with the project's attack-simulation requirements (Kali ships with nmap, hydra, and sqlmap pre-available).

---

## 3. Architecture & Network Integration

### 3.1 Shared Network Design
Discovered that this project's IAM/WAF Docker Compose stack and the SIEM team's Wazuh Compose stack were each defaulting to separate, isolated Docker networks — meaning Wazuh would never have been able to receive logs from WAF or Keycloak, even with both stacks running, with no obvious error to indicate the failure.

**Resolution:** Created one shared external Docker network, `sentrix-net` (subnet `192.168.50.0/24`), and updated both Compose files to attach to it via `external: true`, with static IP assignments:

| IP | Service | Owner |
|---|---|---|
| `.10` / `.11` / `.12` | Wazuh Manager / Indexer / Dashboard | Jagan (Member 1) |
| `.21` | DVWA (target application) | Shared |
| `.40` | WAF (ModSecurity + Nginx) | Member 3 |
| `.50` | Keycloak | Member 3 |
| `.60` | Protected Flask application | Member 3 |

### 3.2 WAF Port Mapping Fix
The `owasp/modsecurity-crs:nginx` image listens internally on port **8080**, not port 80. Initial mapping (`"80:80"`) caused all external requests to silently reset with no response. Corrected to `"80:8080"`. Verified via direct curl test, receiving a proper HTTP 302 redirect from DVWA through the WAF.

---

## 4. Identity & Access Management (Keycloak)

### 4.1 Configuration
- **Realm:** `Fortress-SOC`
- **Roles:** `admin`, `analyst`
- **Client:** `sentrix-app` (OpenID Connect, confidential client, Standard Flow enabled)
- **Protected service:** Custom Flask application (`iam-waf/protected-app`) integrated via OAuth2/OIDC authorization code flow, decoding JWT role claims on login
- **Users:** `admin_1` (role: admin), `analyst_1` (role: analyst)

### 4.2 RBAC Verification (Live, End-to-End)
Both users successfully authenticate through Keycloak via the protected Flask application. Each user's session correctly displays their distinct assigned role, confirmed via direct browser testing:
- `admin_1` → Roles: `['admin', 'offline_access', 'uma_authorization', 'default-roles-fortress-soc']`
- `analyst_1` → Roles: `['analyst', 'offline_access', 'uma_authorization', 'default-roles-fortress-soc']`

This proves the full authentication-to-authorization chain works, not just static configuration.

### 4.3 Brute-Force Protection
Enabled Keycloak's native brute-force detection (Realm Settings → Security Defenses). Configured with a low failure threshold and short lockout window suitable for live demonstration. Verified: repeated failed login attempts against `analyst_1` resulted in temporary account lockout, with manual unlock capability confirmed available via the Keycloak admin console (Users → user → unlock toggle) for demo control.

---

## 5. Web Application Firewall (ModSecurity + Nginx)

### 5.1 Configuration
- **Image:** `owasp/modsecurity-crs:nginx` (OWASP Core Rule Set pre-loaded, 846 rules)
- **Mode:** Reverse proxy in front of DVWA (`192.168.50.21`)
- **Audit logging:** Configured to `/dev/stdout` (image default), captured via `docker logs waf`, in structured JSON format (`SecAuditLogFormat JSON`)
- **Blocking configuration:** `SecAuditEngine RelevantOnly`, inbound anomaly score threshold of 5

### 5.2 Manual SQL Injection Test
Sent a manually crafted SQL injection payload (`' OR '1'='1`) through the WAF to DVWA's SQLi test page.

**Result:**
- OWASP CRS rule `942100` (libinjection SQLi detection) correctly identified the injection in the `id` parameter
- Rule `949110` (Inbound Anomaly Score Exceeded) escalated and blocked the request
- HTTP response: `403 Forbidden`
- Full event logged in structured JSON, captured in `iam-waf/proof-screenshots/waf_sqli_block_proof.log`

### 5.3 Automated SQLMap Attack Test
Ran SQLMap — a real, industry-standard automated SQL injection tool — against DVWA's SQLi endpoint through the WAF:


sqlmap -u "http://localhost/vulnerabilities/sqli/?id=1&Submit=Submit" --batch


**Result:** SQLMap attempted 147 distinct injection requests across multiple technique categories (boolean-based blind, error-based, UNION-based, time-based blind, across MySQL/PostgreSQL/MSSQL/Oracle syntax variants). **All 147 requests were blocked** with HTTP 403. SQLMap's own conclusion: *"all tested parameters do not appear to be injectable."*

Full output captured in `iam-waf/proof-screenshots/sqlmap_attack_proof.log`.

**Important architectural note:** DVWA's SQLi vulnerability is genuinely present and exploitable — confirmed by testing directly against DVWA's internal IP (`192.168.50.21`), bypassing the WAF, where the same attack succeeds. The WAF's value is not that the underlying vulnerability doesn't exist, but that the only externally reachable path (`localhost`, port-mapped through the WAF) is fully gated. DVWA's direct IP is only reachable from within the Kali VM's internal Docker network — never exposed to the host or external network — meaning this bypass path does not exist for a real external attacker.

---

## 6. Brownie Point #2 — "The Loyal Guard Who Lets Everyone In" (Day 2)

### 6.1 Decode
The riddle describes authentication succeeding as a binary identity check — a login that verifies "is this the right credential" but never questions the *pattern* surrounding repeated authentications (same user, multiple times, no behavioral context). Authentication confirms identity; it does not confirm intent or safety.

### 6.2 Implementation
Built a Python service (`iam-waf/anomaly-detector/detector.py`) that polls Keycloak's Admin REST API every 10 seconds for both `LOGIN` and `LOGIN_ERROR` events. It maintains a rolling time-window history per user and raises a distinct, elevated alert — separate from routine login logging — under three conditions:
1. **Off-hours login** (00:00–05:00)
2. **Rapid repeat logins** — 3+ successful logins by the same user within a 5-minute window
3. **Failed login / lockout events** — flagging brute-force lockout triggers as HIGH severity

### 6.3 Live Proof
- Triggered 3 rapid successful logins as `admin_1` within ~2 minutes → detector correctly escalated this into a `HIGH`-severity "Rapid repeat logins" anomaly, distinct from the preceding `INFO`-level entries
- Triggered repeated failed logins as `analyst_1` → Keycloak's native brute-force protection locked the account, and the detector separately logged the `LOGIN_ERROR` / lockout event as a distinct anomaly

Full decode notes and proof in `iam-waf/BROWNIE_POINT_2_COMPLETE.md`.

---

## 7. Problems Encountered and Resolutions

| Problem | Resolution |
|---|---|
| Docker Desktop install failed on Windows | Migrated full stack to Kali Linux VM |
| IAM/WAF and SIEM Compose stacks on isolated networks | Created shared external `sentrix-net` network with static IPs |
| Duplicate top-level `networks:` key in YAML | Identified via `docker compose config` validation, removed duplicate |
| WAF returned connection reset on all requests | Diagnosed via layered testing; found image listens on 8080 internally, fixed port mapping |
| GitHub rejected password authentication | Switched to Personal Access Token over HTTPS (SSH blocked on both port 22 and 443 fallback) |
| ModSecurity audit log file not found at expected path | Found logs are written to `/dev/stdout` by this image; read via `docker logs waf` instead |
| `.gitignore`'s `*.log` rule silently blocked proof log commits | Added targeted exception (`!iam-waf/proof-screenshots/*.log`) |
| Browser session/saved password prevented repeated login testing | Used private/incognito windows and Keycloak's direct logout endpoint to force fresh sessions |
| Anomaly detector missed failed-login/lockout events | Extended event polling from `LOGIN`-only to include `LOGIN_ERROR` |

---

## 8. Current Status

**Complete and verified:**
- IAM (Keycloak) — realm, roles, client, RBAC, brute-force protection
- WAF (ModSecurity + Nginx) — reverse proxy, manual SQLi block, automated SQLMap block (147/147)
- Brownie Point #2 — fully implemented, decoded, and proven live
- Shared network architecture connecting IAM/WAF stack to SIEM stack

**Pending — blocked on external dependency:**
- Wazuh Manager/Indexer/Dashboard (owned by Jagan, Member 1) is not yet confirmed running/reachable on the shared network (`192.168.50.10` / `.12`)
- Once Jagan's Wazuh stack is up, the following remaining tasks will be completed:
  1. Install Wazuh agent on the WAF/Keycloak host
  2. Forward WAF audit logs (script pre-built: `iam-waf/forward-waf-logs.sh`) and Keycloak login/anomaly events into Wazuh
  3. Confirm both appear in the Wazuh dashboard as distinct, identifiable sources (separate from Suricata)
  4. Re-run the SQLMap and brute-force tests and confirm both are visible in the SIEM dashboard — the final cross-layer proof requirement

All work in this document is independently verifiable via the proof logs and scripts committed to `iam-waf/` in this repository.
