#!/bin/sh
ROOT=$(cd "$(dirname "$0")/.." && pwd)
BIN=$(mktemp)
DUMP=$(mktemp)
trap 'rm -f "$BIN" "$DUMP"' EXIT

echo "\$ run.sh examples/copy_array.yaml program.bin"
sh "$ROOT/run.sh" "$ROOT/examples/copy_array.yaml" "$BIN" || exit 1
echo
echo "\$ run_interpreter.sh program.bin dump.xml --range 10 24"
sh "$ROOT/run_interpreter.sh" "$BIN" "$DUMP" --range 10 24 || exit 1
echo
echo "\$ cat dump.xml"
cat "$DUMP"
