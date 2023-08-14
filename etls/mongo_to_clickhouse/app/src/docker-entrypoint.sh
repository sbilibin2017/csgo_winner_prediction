#!/bin/bash

echo "Waiting for postgres..."
while ! nc -z db ${POSTGRES_PORT}; do
  sleep 0.1
done
echo "PostgreSQL started"

export FLASK_APP=main.py

echo "Starting flask app ..."
gunicorn --bind 0.0.0.0:${APP_PORT} main:app