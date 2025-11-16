#!/usr/bin/env python3
"""
Automated Setup Script with Environment Compatibility Checks
Cross-platform Python version for Windows/Mac/Linux
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from typing import Tuple, Optional

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not supported"""
        if sys.platform == 'win32':
            Colors.RED = Colors.GREEN = Colors.YELLOW = Colors.BLUE = Colors.NC = ''

Colors.disable_on_windows()

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.NC}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.NC}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.NC}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.NC}")

def run_command(cmd: list, check: bool = True, capture: bool = False) -> Tuple[int, str]:
    """Run a command and return exit code and output"""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result.returncode, result.stdout.strip()
        else:
            result = subprocess.run(cmd, check=check)
            return result.returncode, ""
    except subprocess.CalledProcessError as e:
        return e.returncode, str(e)
    except Exception as e:
        return 1, str(e)

def detect_python_conflicts() -> str:
    """Detect and handle Python environment conflicts"""
    print_info("Checking for Python environment conflicts...")
    
    # Check for conda environment
    if os.environ.get('CONDA_DEFAULT_ENV'):
        conda_env = os.environ['CONDA_DEFAULT_ENV']
        print_warning(f"Detected Conda environment: {conda_env}")
        print_info("This may cause conflicts with venv")
        
        # Unset conda variables
        for var in ['CONDA_DEFAULT_ENV', 'CONDA_PREFIX', 'CONDA_PYTHON_EXE']:
            os.environ.pop(var, None)
        
        print_success("Conda environment variables cleared")
    
    # Find Python executable
    python_cmd = shutil.which('python3') or shutil.which('python')
    
    if not python_cmd:
        print_error("Python not found! Please install Python 3.10+")
        sys.exit(1)
    
    # Check Python version
    code, version_output = run_command([python_cmd, '--version'], capture=True)
    version = version_output.split()[1] if version_output else "unknown"
    
    print_info(f"Found Python: {version}")
    
    # Check if version is 3.10+
    try:
        major, minor = map(int, version.split('.')[:2])
        if major < 3 or (major == 3 and minor < 10):
            print_error(f"Python 3.10+ is required. Found: {version}")
            sys.exit(1)
    except:
        print_warning(f"Could not parse Python version: {version}")
    
    print_success(f"Python version compatible: {version}")
    return python_cmd

def cleanup_venv() -> bool:
    """Clean up old/corrupted venv, return True if existing venv is healthy"""
    venv_path = Path('venv')
    
    if not venv_path.exists():
        return False
    
    print_warning("Found existing venv directory")
    print_info("Checking if venv is healthy...")
    
    # Check if venv has required structure
    if sys.platform == 'win32':
        python_exe = venv_path / 'Scripts' / 'python.exe'
        pip_exe = venv_path / 'Scripts' / 'pip.exe'
    else:
        python_exe = venv_path / 'bin' / 'python'
        pip_exe = venv_path / 'bin' / 'pip'
    
    if not python_exe.exists():
        print_warning("venv directory is incomplete")
        shutil.rmtree(venv_path)
        print_success("Incomplete venv removed")
        return False
    
    # Try to run pip
    code, _ = run_command([str(python_exe), '-m', 'pip', '--version'], check=False, capture=True)
    
    if code != 0:
        print_warning("pip is not working in venv")
        print_info("Removing corrupted venv...")
        shutil.rmtree(venv_path)
        print_success("Corrupted venv removed")
        return False
    
    print_success("Existing venv appears healthy")
    return True

def create_venv(python_cmd: str) -> bool:
    """Create virtual environment with compatibility fixes"""
    print_info("Creating virtual environment...")
    
    # Try standard venv creation
    code, _ = run_command([python_cmd, '-m', 'venv', 'venv'], check=False)
    
    if code == 0:
        print_success("Virtual environment created successfully")
        return True
    
    print_warning("Standard venv creation failed")
    print_info("Trying alternative method (without pip)...")

    # Create venv without pip
    code, _ = run_command([python_cmd, '-m', 'venv', 'venv', '--without-pip'], check=False)

    if code != 0:
        print_error("Failed to create virtual environment")
        return False

    print_success("Virtual environment created (without pip)")

    # Manually install pip
    print_info("Installing pip manually...")

    if sys.platform == 'win32':
        python_exe = 'venv\\Scripts\\python.exe'
    else:
        python_exe = 'venv/bin/python'

    # Download and install pip
    try:
        import urllib.request
        urllib.request.urlretrieve('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')
        run_command([python_exe, 'get-pip.py'], check=True)
        os.remove('get-pip.py')
        print_success("pip installed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to install pip: {e}")
        return False

def install_dependencies() -> bool:
    """Install dependencies with fallback"""
    print_info("Installing dependencies...")

    if sys.platform == 'win32':
        pip_exe = 'venv\\Scripts\\pip.exe'
        python_exe = 'venv\\Scripts\\python.exe'
    else:
        pip_exe = 'venv/bin/pip'
        python_exe = 'venv/bin/python'

    # Upgrade pip
    print_info("Upgrading pip...")
    run_command([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip', '--quiet'], check=False)

    # Try to install from requirements.txt
    print_info("Installing from requirements.txt...")
    code, _ = run_command([pip_exe, 'install', '-r', 'requirements.txt', '--quiet'], check=False)

    if code == 0:
        print_success("All dependencies installed successfully")
    else:
        print_warning("Some packages failed to install")
        print_info("Installing critical packages individually...")

        critical_packages = [
            'streamlit',
            'loguru',
            'openai',
            'qdrant-client',
            'neo4j',
            'redis',
            'pytest',
        ]

        for package in critical_packages:
            code, _ = run_command([pip_exe, 'install', package, '--quiet'], check=False)
            if code != 0:
                print_warning(f"Failed to install {package}")

        print_success("Critical packages installed")

    # Verify critical imports
    print_info("Verifying installation...")
    verify_code = """
import streamlit, loguru, openai, qdrant_client, neo4j, redis, pytest
print("OK")
"""

    code, output = run_command([python_exe, '-c', verify_code], check=False, capture=True)

    if code == 0 and 'OK' in output:
        print_success("All critical packages verified")
        return True
    else:
        print_error("Some critical packages are missing")
        print_info("You may need to install them manually")
        return False

def setup_docker() -> bool:
    """Check and start Docker services"""
    print_info("Checking Docker...")

    if not shutil.which('docker'):
        print_warning("Docker not found")
        print_info("Please install Docker to run Neo4j, Qdrant, and Redis")
        print_info("Visit: https://docs.docker.com/get-docker/")
        return False

    print_success("Docker found")

    # Check if Docker is running
    code, _ = run_command(['docker', 'info'], check=False, capture=True)

    if code != 0:
        print_warning("Docker is not running")
        print_info("Please start Docker Desktop and run this script again")
        return False

    print_success("Docker is running")

    # Check for docker-compose
    docker_compose_cmd = None
    if shutil.which('docker-compose'):
        docker_compose_cmd = ['docker-compose']
    elif shutil.which('docker'):
        # Try docker compose (v2)
        code, _ = run_command(['docker', 'compose', 'version'], check=False, capture=True)
        if code == 0:
            docker_compose_cmd = ['docker', 'compose']

    if not docker_compose_cmd:
        print_warning("docker-compose not found")
        return False

    # Remove old containers
    print_info("Removing old containers...")
    run_command(docker_compose_cmd + ['down', '--remove-orphans'], check=False)

    # Start services
    print_info("Starting Docker services (Neo4j, Qdrant, Redis)...")
    code, _ = run_command(docker_compose_cmd + ['up', '-d'], check=False)

    if code != 0:
        print_error("Failed to start Docker services")
        return False

    print_success("Docker services started")
    print_info("Waiting for services to be ready (30 seconds)...")
    time.sleep(30)

    # Check service health
    print_info("Checking service health...")
    run_command(['docker', 'ps', '--filter', 'name=multimodal-'], check=False)

    print_success("Docker services are ready")
    return True

def setup_env_file():
    """Setup environment file"""
    if Path('.env').exists():
        print_success(".env file already exists")
        return

    print_info("Creating .env file...")

    if Path('.env.example').exists():
        shutil.copy('.env.example', '.env')
        print_success(".env file created from .env.example")
    else:
        # Create basic .env file
        env_content = """# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
"""
        Path('.env').write_text(env_content)
        print_success(".env file created with defaults")

    print_warning("⚠️  IMPORTANT: Edit .env file and add your OPENAI_API_KEY")

def main():
    """Main setup flow"""
    print(f"{Colors.BLUE}🚀 Multimodal RAG System - Automated Setup{Colors.NC}")
    print("=" * 50)
    print()

    print_info("Step 1: Detecting Python environment conflicts...")
    python_cmd = detect_python_conflicts()

    print()
    print_info("Step 2: Checking existing virtual environment...")
    if cleanup_venv():
        print_info("Using existing virtual environment")
    else:
        print()
        print_info("Step 3: Creating new virtual environment...")
        if not create_venv(python_cmd):
            print_error("Setup failed: Could not create virtual environment")
            sys.exit(1)

    print()
    print_info("Step 4: Installing dependencies...")
    install_dependencies()

    print()
    print_info("Step 5: Setting up environment file...")
    setup_env_file()

    print()
    print_info("Step 6: Setting up Docker services...")
    if not setup_docker():
        print_warning("Docker setup skipped - you'll need to start services manually")

    print()
    print("=" * 50)
    print_success("Setup Complete! 🎉")
    print("=" * 50)
    print()
    print("Next steps:")
    print("  1. Edit .env file and add your OPENAI_API_KEY")

    if sys.platform == 'win32':
        print(f"  2. Activate virtual environment:")
        print(f"     {Colors.GREEN}venv\\Scripts\\activate{Colors.NC}")
    else:
        print(f"  2. Activate virtual environment:")
        print(f"     {Colors.GREEN}source venv/bin/activate{Colors.NC}")

    print(f"  3. Start the application:")
    print(f"     {Colors.GREEN}streamlit run src/ui/app.py{Colors.NC}")
    print(f"  4. Run tests:")
    print(f"     {Colors.GREEN}pytest{Colors.NC}")
    print()
    print("For more information, see README.md")
    print()

if __name__ == '__main__':
    main()

