#!/bin/bash
BACKEND_PORT=5001
TUNNEL_BIN=/tmp/cloudflared
TUNNEL_LOG=/tmp/cflog.txt
BACKEND_DIR=/home/yasin/ai-stock-tracker/backend
BACKEND_LOG=/tmp/backend.log

restart_tunnel() {
    pkill -f "$TUNNEL_BIN tunnel" 2>/dev/null
    sleep 1
    nohup "$TUNNEL_BIN" tunnel --url "http://localhost:$BACKEND_PORT" > "$TUNNEL_LOG" 2>&1 &
    echo "[watchdog] tunnel restarted at $(date)" >> /tmp/watchdog.log
}

restart_backend() {
    fuser -k "$BACKEND_PORT/tcp" 2>/dev/null
    sleep 1
    nohup python3 "$BACKEND_DIR/app.py" > "$BACKEND_LOG" 2>&1 &
    echo "[watchdog] backend restarted at $(date)" >> /tmp/watchdog.log
    sleep 3
}

while true; do
    # 1. check backend
    if ! curl -sf "http://localhost:$BACKEND_PORT/" >/dev/null 2>&1; then
        echo "[watchdog] backend down, restarting..." >> /tmp/watchdog.log
        restart_backend
        restart_tunnel
        sleep 30
        continue
    fi

    # 2. check tunnel process
    if ! pgrep -f "$TUNNEL_BIN tunnel" >/dev/null 2>&1; then
        echo "[watchdog] tunnel process dead, restarting..." >> /tmp/watchdog.log
        restart_tunnel
        sleep 30
        continue
    fi

    # 3. check tunnel reachable
    TUNNEL_URL=$(grep -o 'https://[a-z0-9.-]*\.trycloudflare\.com' "$TUNNEL_LOG" 2>/dev/null | tail -1)
    if [ -n "$TUNNEL_URL" ]; then
        if ! curl -sfo /dev/null "$TUNNEL_URL" >/dev/null 2>&1; then
            echo "[watchdog] tunnel unreachable ($TUNNEL_URL), restarting..." >> /tmp/watchdog.log
            restart_tunnel
        fi
    fi

    sleep 30
done
