#!/bin/bash

while ! nc -z clickhouse_server ${CLICKHOUSE_SERVER_PORT}; do
  echo "Waiting for clickhouse server..."
  sleep 1
done
echo "Clickhouse server started"

python3 main.py