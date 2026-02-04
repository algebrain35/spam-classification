#!/bin/bash

set -e

redis-server --daemonize yes

shutdown() {
  echo "Shutting down..."
  pkill -f "uvicorn"
  pkill -f "python worker.py" || true
  wait
  exit 0
}

trap shutdown SIGTERM SIGINT
uvicorn main:app --host 0.0.0.0 --port 8000&
SERVER_PID=$!

sleep 2
python worker.py &
WORKER_PID=$!

wait -n
kill $SERVER_PID $WORKER_PID 2>/dev/null || true
wait

echo "One process exited. Stopping container..."
exit 1
