# Wazuh Indexer Compatibility Issue — Day 2

## Problem

Wazuh Indexer (OpenSearch 2.8.0) fails to run on Apple M1 (ARM64).

## Root Cause

- Wazuh Indexer Docker image is built for AMD64 (x86) architecture

- Mac M1 uses ARM64 (aarch64) architecture

- Docker Rosetta emulation lacks required Linux kernel features:

  - CONFIG_SECCOMP not available in emulated environment

  - syscall filters unavailable

  - OpenSearch crashes immediately on startup

## Evidence

Error from logs:

java.lang.UnsupportedOperationException: seccomp unavailable: 

CONFIG_SECCOMP not compiled into kernel

## Solutions Attempted

1. Increased Java heap: -Xms1g -Xmx1g → still crashed

2. Added seccomp:unconfined flag → still crashed

3. Tried running inside Ubuntu UTM VM → also ARM64, same issue

4. All attempts failed due to architecture incompatibility

## Final Solution

Moving Wazuh Indexer + Dashboard to Member 4's Windows laptop

- Windows = x86 native AMD64

- No emulation needed

- Full kernel support available

- 8GB RAM sufficient for indexer + dashboard only

## Current Status

- Wazuh Manager: Running on Mac M1 ✅

- Wazuh Indexer: Being deployed on dedicated x86 Windows machine

- Wazuh Dashboard: Pending indexer connection

- All agents: Registered and sending logs ✅

- Suricata alerts: Flowing into Manager ✅
