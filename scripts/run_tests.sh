#!/bin/sh
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT" || exit 1
PYTHONPATH=src exec python3 -m unittest discover -s tests -v
