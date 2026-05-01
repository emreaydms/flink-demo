#!/usr/bin/env bash
# run_demo.sh — One-command demo runner for the Apache Flink examples
#
# Usage:
#   ./run_demo.sh wordcount      # streaming word count (interactive)
#   ./run_demo.sh fraud          # fraud detection on simulated data
#   ./run_demo.sh stop           # stop and remove all containers
#
# Prerequisites: Docker Desktop running, .env file present
#   cp .env.example .env

set -e

DEMO=${1:-fraud}

check_env() {
  if [ ! -f .env ]; then
    echo "⚠  .env not found. Copying from .env.example..."
    cp .env.example .env
  fi
}

start_cluster() {
  echo "▶  Starting Flink cluster (JobManager + TaskManager)..."
  docker-compose up -d jobmanager taskmanager
  echo "⏳  Waiting for cluster to be ready..."
  sleep 8
  echo "✅  Flink Web UI: http://localhost:8081"
}

case "$DEMO" in
  wordcount)
    check_env
    start_cluster

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  WORD COUNT DEMO"
    echo "  Open a NEW terminal and run:"
    echo "    nc -lk 9999"
    echo "  Then type words and press Enter to see live counts."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    docker-compose run --rm pyflink bash -c "
      pip install apache-flink==1.18.1 -q 2>/dev/null || true
      python word_count.py
    "
    ;;

  fraud)
    check_env
    start_cluster

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  FRAUD DETECTION DEMO"
    echo "  Processing simulated transaction stream..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    docker-compose run --rm pyflink bash -c "
      pip install apache-flink==1.18.1 -q 2>/dev/null || true
      python fraud_detection.py
    "
    ;;

  stop)
    echo "⏹  Stopping Flink cluster..."
    docker-compose down
    echo "✅  All containers stopped."
    ;;

  *)
    echo "Usage: $0 {wordcount|fraud|stop}"
    exit 1
    ;;
esac
