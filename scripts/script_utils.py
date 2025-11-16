"""Utility functions for scripts to ensure proper environment setup."""

import sys
import os
from pathlib import Path


def setup_environment():
    """
    Set up the environment for scripts.
    
    This function:
    1. Adds the project root to sys.path
    2. Changes working directory to project root
    3. Loads environment variables from .env file
    
    Returns:
        Path: The project root directory
    """
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent.resolve()
    
    # Add to Python path if not already there
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Load environment variables from .env file
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    else:
        print(f"⚠️  Warning: .env file not found at {env_path}")
        print("   Some features may not work without environment variables.")
    
    return project_root


def verify_api_key():
    """
    Verify that the OpenAI API key is loaded.
    
    Returns:
        bool: True if API key is loaded, False otherwise
    """
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Please ensure your .env file contains:")
        print("   OPENAI_API_KEY=sk-your-key-here")
        return False
    
    if len(api_key) < 20:
        print("❌ Error: OPENAI_API_KEY appears to be invalid (too short)")
        return False
    
    print(f"✅ OpenAI API key loaded: {api_key[:15]}...{api_key[-8:]}")
    return True


def check_services():
    """
    Check if required services (Neo4j, Qdrant) are running.

    Returns:
        dict: Status of each service
    """
    import socket

    services = {
        'neo4j': ('localhost', 7687),
        'qdrant': ('localhost', 6333),
        'redis': ('localhost', 6379)
    }

    status = {}

    for service_name, (host, port) in services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                status[service_name] = True
                print(f"✅ {service_name.capitalize()} is running on {host}:{port}")
            else:
                status[service_name] = False
                print(f"❌ {service_name.capitalize()} is NOT running on {host}:{port}")
        except Exception as e:
            status[service_name] = False
            print(f"❌ Error checking {service_name}: {e}")

    return status


def check_ffmpeg():
    """
    Check if FFmpeg is installed (required for audio/video processing).

    Returns:
        bool: True if FFmpeg is installed, False otherwise
    """
    import subprocess

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg is installed: {version_line}")
            return True
        else:
            print("❌ FFmpeg is installed but not working properly")
            return False

    except FileNotFoundError:
        print("❌ FFmpeg is NOT installed")
        print("   Audio/video processing will not work without FFmpeg")
        print("   Install it with:")
        print("   - macOS: brew install ffmpeg")
        print("   - Ubuntu: sudo apt install ffmpeg")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False

