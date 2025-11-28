#!/usr/bin/env bash
set -euo pipefail

ARGS="$@"
if [ -z "$ARGS" ]; then
  ARGS="-vv"
fi

echo "[run-tests] pytest $ARGS"
DOCKER_BUILDKIT=1 docker compose build tests
DOCKER_BUILDKIT=1 docker compose run --rm tests bash -lc "pip install -r requirements-dev.txt >/tmp/install.log && PYTHONPATH=/workspace pytest $ARGS"
