#!/bin/sh
# Run `pros update` from this clone.
exec python3 "$(dirname "$0")/../pros.py" update "$@"
