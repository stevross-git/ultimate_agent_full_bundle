#!/bin/bash
# Enhanced Node Server Security Monitor

LOG_FILE="/var/log/enhanced-node-security.log"
ALERT_EMAIL="admin@peoplesainetwork.com"

# Function to log with timestamp
log_alert() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - SECURITY ALERT: $1" >> $LOG_FILE
}

# Monitor for SSL/TLS attacks
tail -F /var/log/nginx/srvnodes.error.log | while read line; do
    # Check for SSL probe attempts
    if echo "$line" | grep -q "SSL_ERROR\|bad request\|400"; then
        IP=$(echo "$line" | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
        log_alert "SSL probe attempt from $IP: $line"
        
        # Auto-block persistent attackers
        if [ ! -z "$IP" ]; then
            COUNT=$(grep "$IP" $LOG_FILE | wc -l)
            if [ $COUNT -gt 5 ]; then
                sudo ufw deny from $IP
                log_alert "Auto-blocked IP $IP after $COUNT attempts"
            fi
        fi
    fi
    
    # Check for WebSocket abuse
    if echo "$line" | grep -q "websocket\|socket.io" && echo "$line" | grep -q "error\|failed"; then
        IP=$(echo "$line" | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
        log_alert "WebSocket abuse attempt from $IP: $line"
    fi
done &

# Monitor Enhanced Node Server logs
tail -F /opt/enhanced-node/logs/*.log | while read line; do
    # Check for authentication failures
    if echo "$line" | grep -q "authentication failed\|unauthorized\|forbidden"; then
        log_alert "Authentication failure: $line"
    fi
    
    # Check for command injection attempts
    if echo "$line" | grep -q "command injection\|script injection\|payload"; then
        log_alert "Injection attempt: $line"
    fi
done &

echo "Security monitoring started..."