#!/bin/bash
# start_app.sh - Start Gunicorn app service

export LI_STORE_ROOTS=../experiments/
TVST_MOUNT=/
TVST_HOST=127.0.0.1
TVST_PORT=8084
WORKERS=2
APP_MODULE=linnea_inspector.widget.inspector:app

mkdir -p tmp/

PID_FILE=tmp/gunicorn_app.pid
LOG_FILE=tmp/gunicorn_app.log

# Check if already running
if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
  echo "Gunicorn already running with PID $(cat $PID_FILE)"
  exit 0
fi

echo "Starting Gunicorn..."
TVST_MOUNT=$TVST_MOUNT gunicorn -w "$WORKERS" -b "$TVST_HOST:$TVST_PORT" "$APP_MODULE" \
  --limit-request-field_size 16380 --pid "$PID_FILE" --daemon --log-file "$LOG_FILE" --log-level info

sleep 1
if kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
  echo "Gunicorn started successfully (PID $(cat $PID_FILE))"
else
  echo "Failed to start Gunicorn (check $LOG_FILE)"
fi
