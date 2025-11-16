#!/usr/bin/env python3
"""Restart Streamlit app and clear all caches."""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

def kill_streamlit():
    """Kill any running Streamlit processes."""
    print("\n1. Stopping existing Streamlit processes...")
    
    # Kill by process name
    subprocess.run(["pkill", "-f", "streamlit run"], stderr=subprocess.DEVNULL)
    
    # Kill by port
    try:
        result = subprocess.run(
            ["lsof", "-ti:8501"],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(["kill", "-9", pid], stderr=subprocess.DEVNULL)
    except Exception:
        pass
    
    time.sleep(2)
    print("   ✅ Stopped")


def clear_python_cache():
    """Clear Python bytecode cache."""
    print("\n2. Clearing Python bytecode cache...")
    
    project_root = Path.cwd()
    
    # Remove __pycache__ directories
    for pycache_dir in project_root.rglob("__pycache__"):
        try:
            shutil.rmtree(pycache_dir)
        except Exception:
            pass
    
    # Remove .pyc files
    for pyc_file in project_root.rglob("*.pyc"):
        try:
            pyc_file.unlink()
        except Exception:
            pass
    
    print("   ✅ Cleared __pycache__")


def clear_streamlit_cache():
    """Clear Streamlit cache."""
    print("\n3. Clearing Streamlit cache...")
    
    streamlit_cache = Path.home() / ".streamlit" / "cache"
    if streamlit_cache.exists():
        try:
            shutil.rmtree(streamlit_cache)
        except Exception:
            pass
    
    print("   ✅ Cleared Streamlit cache")


def start_streamlit():
    """Start Streamlit app."""
    print("\n4. Starting Streamlit app...")
    print("   URL: http://localhost:8501")
    print("\n" + "=" * 50)
    print("Starting in 3 seconds...")
    print("=" * 50)
    
    time.sleep(3)
    
    # Start Streamlit
    subprocess.Popen(
        ["streamlit", "run", "src/ui/app.py", "--server.port", "8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("\n✅ Streamlit started!")
    print("\n📝 Next steps:")
    print("   1. Wait 5-10 seconds for the app to start")
    print("   2. Open http://localhost:8501 in your browser")
    print("   3. Try uploading the video again")
    print("\nTo stop Streamlit:")
    print("   pkill -f streamlit")
    print()


def main():
    """Main entry point."""
    print("=" * 50)
    print("Restarting Streamlit App")
    print("=" * 50)
    
    kill_streamlit()
    clear_python_cache()
    clear_streamlit_cache()
    
    time.sleep(1)
    
    start_streamlit()


if __name__ == "__main__":
    main()

