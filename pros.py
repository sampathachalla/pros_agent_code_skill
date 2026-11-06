#!/usr/bin/env python3
"""Entry point for the Pros Toolkit CLI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pros_toolkit.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
