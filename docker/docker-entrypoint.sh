#!/bin/sh

set -o errexit
set -o nounset

echo "Docker entrypoint script running..."

check_db() {
python << END
import os
import sys
import psycopg

try:
    conn = psycopg.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
    )
except psycopg.OperationalError as e:
    print(f"PostgreSQL connection failed: {e}")
    sys.exit(-1)

print("Postgres is up - continuing...")
sys.exit(0)
END
}

check_kafka() {
  python << 'END'
import os, sys, socket, json

raw = os.getenv('KAFKA_BOOTSTRAP_SERVERS', '[]')
try:
    servers = json.loads(raw)
    server = servers[0]
except Exception:
    server = raw.split(',')[0].strip()

if server.startswith("tcp://"):
    server = server[len("tcp://"):]

host, port_str = server.split(":", 1)
port = int(port_str)

sock = socket.socket()
sock.settimeout(5)
try:
    sock.connect((host, port))
    print("Kafka is up - continuing...")
    sys.exit(0)
except Exception as e:
    print(f"Kafka connection failed: {e}")
    sys.exit(1)
finally:
    sock.close()
END
}

# Waiting for a DB
echo "Checking PostgreSQL readiness..."
until check_db; do
    echo "PostgreSQL is unavailable - waiting..."
    sleep 1
done

# Migrations running
echo "Running migrations…"
alembic upgrade head

# Waiting for Kafka
echo "Checking Kafka readiness..."
until check_kafka; do
  echo "Kafka is unavailable - waiting..."
  sleep 1
done

# Application startup
echo "Starting application…"
if [ "${DEBUG:-0}" = "1" ]; then
    echo "Running in DEBUG mode with auto-reload"
    watchfiles "python -m src.core.entrypoint" --sigint
else
    python -m src.core.entrypoint
fi
