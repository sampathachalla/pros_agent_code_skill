#!/bin/sh
# Install the toolkit globally. Accepts the options of `pros install`.
set -e
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }
command -v git >/dev/null || { echo "git is required" >&2; exit 1; }
exec python3 "$(dirname "$0")/../pros.py" install "$@"
