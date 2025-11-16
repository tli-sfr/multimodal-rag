#!/usr/bin/env python3
"""Test if imports work correctly."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    from src.pipeline import MultimodalRAGPipeline
    print("✅ Pipeline import successful!")
except Exception as e:
    print(f"❌ Pipeline import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from src.models import Document, Query, Answer
    print("✅ Models import successful!")
except Exception as e:
    print(f"❌ Models import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All imports successful!")

