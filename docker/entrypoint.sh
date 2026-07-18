#!/bin/sh
set -eu

uvicorn app.main:app --host 127.0.0.1 --port 8000 &
api_pid=$!

shutdown() {
    kill -TERM "$api_pid" 2>/dev/null || true
    nginx -s quit 2>/dev/null || true
}

trap shutdown INT TERM EXIT

nginx -g "daemon off;" &
nginx_pid=$!

while kill -0 "$api_pid" 2>/dev/null && kill -0 "$nginx_pid" 2>/dev/null; do
    sleep 1
done

if ! kill -0 "$api_pid" 2>/dev/null; then
    wait "$api_pid"
else
    wait "$nginx_pid"
fi
