#!/bin/sh
set -e

# local sets RELOAD=true to restart on code changes.
if [ "$RELOAD" = "true" ]; then
    set -- --reload
fi

alembic upgrade head

exec uvicorn packages.main:app --host 0.0.0.0 --port "${PORT:-80}" "$@"
