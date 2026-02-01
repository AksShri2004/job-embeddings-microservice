#!/bin/bash
# Remove old logs
rm -f server.log
# Run server, redirecting output to server.log, backgrounded
nohup python3 -m src.main > server.log 2>&1 &
# Save PID
echo $! > server.pid
echo "Server starting..."
