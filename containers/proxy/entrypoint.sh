#!/bin/sh

# Check if all necessary environment variables are set
if [ -z "$LOCAL_PORT" ] || [ -z "$LOCAL_ADDRESS" ] || [ -z "$REMOTE_PORT" ] || [ -z "$REMOTE_ADDRESS" ]; then
    echo "Error: Required environment variables (LOCAL_PORT, LOCAL_ADDRESS, REMOTE_PORT, REMOTE_ADDRESS) are not set."
    exit 1
fi

# Create the HAProxy configuration file
cat <<EOF > /usr/local/etc/haproxy/haproxy.cfg
global
    log stdout format raw local0

defaults
    log     global
    mode    tcp
    option  tcplog
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

frontend ft_tcp
    bind "$LOCAL_ADDRESS":$LOCAL_PORT
    default_backend bk_tcp

backend bk_tcp
    server server1 $REMOTE_ADDRESS:$REMOTE_PORT maxconn 32
EOF

# Run HAProxy
haproxy -f /usr/local/etc/haproxy/haproxy.cfg
