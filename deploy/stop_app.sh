#!/bin/bash
# stop_app.sh - Stop Gunicorn app service
deactivate
PID_FILE=tmp/gunicorn_app.pid

if [ ! -f "$PID_FILE" ]; then
  echo "No PID file found. Gunicorn may not be running."
  exit 0
fi

PID=$(cat "$PID_FILE")

if kill -0 "$PID" 2>/dev/null; then
  echo "Stopping Gunicorn (PID $PID)..."
  kill "$PID"
  sleep 2
  if kill -0 "$PID" 2>/dev/null; then
    echo "Process still alive. Forcing termination..."
    kill -9 "$PID"
  fi
  echo "Stopped."
else
  echo "Process with PID $PID not running."
fi

rm -f "$PID_FILE"