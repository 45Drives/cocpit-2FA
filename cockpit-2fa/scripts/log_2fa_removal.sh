#!/bin/bash

USER="$1"
ACTOR="$2"
LOG_FILE="/var/log/2fa_removal.log"

# Create the log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    chown root:root "$LOG_FILE"
    chmod 600 "$LOG_FILE"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - 2FA removed for user: $USER by $ACTOR" >> "$LOG_FILE"
