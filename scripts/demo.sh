#!/bin/sh
ROOT=$(cd "$(dirname "$0")/.." && pwd)

show() {
    echo "\$ run.sh $*"
    sh "$ROOT/run.sh" "$@"
    echo "код завершения: $?"
    echo
}

show "$ROOT/examples/spec_tests.yaml" result.bin --test
show "$ROOT/examples/commented.yaml" result.bin --test
show "$ROOT/examples/invalid_range.yaml" result.bin --test
