#!/bin/bash
LOGFILE="/var/log/waf_forwarded.log"
touch $LOGFILE
docker logs -f waf >> $LOGFILE 2>&1
