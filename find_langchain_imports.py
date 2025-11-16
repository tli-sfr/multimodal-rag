#!/usr/bin/env python3
"""Find all langchain imports in src directory."""

import os
from pathlib import Path

project_root = Path(__file__).parent
src_dir = project_root / "src"

print("Searching for langchain imports in src/...")
print()

for py_file in src_dir.rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    
    with open(py_file, 'r') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        if "from langchain." in line or "import langchain." in line:
            print(f"{py_file}:{line_num}: {line.strip()}")

print()
print("Search complete!")

