#!/bin/sh
# Run `pros uninstall` from this clone.
exec python3 "$(dirname "$0")/../pros.py" uninstall "$@"
