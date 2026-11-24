#!/bin/sh
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT=$(mktemp)
trap 'rm -f "$OUT"' EXIT

show() {
    echo "\$ run.sh $1 result.bin --test"
    sh "$ROOT/run.sh" "$ROOT/examples/$1" "$OUT" --test
    echo "код завершения: $?"
    echo
}

show spec_tests.yaml
show commented.yaml
show invalid_range.yaml
