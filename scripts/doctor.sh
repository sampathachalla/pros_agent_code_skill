#!/bin/sh
# Run `pros doctor` from this clone.
exec python3 "$(dirname "$0")/../pros.py" doctor "$@"
