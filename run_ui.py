#!/usr/bin/env python3
"""Launcher script for Streamlit UI."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    # Run streamlit with the app file
    app_file = project_root / "src" / "ui" / "app.py"
    sys.argv = ["streamlit", "run", str(app_file)]
    sys.exit(stcli.main())

