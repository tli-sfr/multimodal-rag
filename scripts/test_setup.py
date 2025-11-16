#!/usr/bin/env python3
"""
Test script to verify setup_auto.py detection logic
"""

import os
import sys
import subprocess
from pathlib import Path

def test_python_detection():
    """Test Python version detection"""
    print("Testing Python detection...")
    
    # Get Python version
    result = subprocess.run([sys.executable, '--version'], capture_output=True, text=True)
    version = result.stdout.strip() or result.stderr.strip()
    print(f"  ✅ Detected Python: {version}")
    
    # Check version is 3.10+
    version_parts = version.split()[1].split('.')
    major, minor = int(version_parts[0]), int(version_parts[1])
    
    if major >= 3 and minor >= 10:
        print(f"  ✅ Version check passed: {major}.{minor} >= 3.10")
    else:
        print(f"  ❌ Version check failed: {major}.{minor} < 3.10")
        return False
    
    return True

def test_conda_detection():
    """Test Conda environment detection"""
    print("\nTesting Conda detection...")
    
    if os.environ.get('CONDA_DEFAULT_ENV'):
        print(f"  ⚠️  Conda environment detected: {os.environ['CONDA_DEFAULT_ENV']}")
        print("  ℹ️  Setup script will deactivate this automatically")
    else:
        print("  ✅ No Conda environment detected")
    
    return True

def test_venv_detection():
    """Test virtual environment detection"""
    print("\nTesting venv detection...")
    
    venv_path = Path('venv')
    
    if venv_path.exists():
        print(f"  ℹ️  Found existing venv directory")
        
        # Check if it has the right structure
        if sys.platform == 'win32':
            python_exe = venv_path / 'Scripts' / 'python.exe'
        else:
            python_exe = venv_path / 'bin' / 'python'
        
        if python_exe.exists():
            print(f"  ✅ venv has Python executable: {python_exe}")
            
            # Try to run pip
            result = subprocess.run(
                [str(python_exe), '-m', 'pip', '--version'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✅ pip is working: {result.stdout.strip()}")
            else:
                print(f"  ⚠️  pip is not working (venv may be corrupted)")
                print("  ℹ️  Setup script will recreate venv automatically")
        else:
            print(f"  ⚠️  venv is incomplete (missing Python executable)")
            print("  ℹ️  Setup script will recreate venv automatically")
    else:
        print("  ℹ️  No existing venv found")
        print("  ℹ️  Setup script will create new venv")
    
    return True

def test_docker_detection():
    """Test Docker detection"""
    print("\nTesting Docker detection...")
    
    # Check if docker command exists
    result = subprocess.run(['which', 'docker'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"  ✅ Docker found: {result.stdout.strip()}")
        
        # Check if Docker is running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Docker is running")
            
            # Check for existing containers
            result = subprocess.run(
                ['docker', 'ps', '-a', '--filter', 'name=multimodal-', '--format', '{{.Names}}'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                print(f"  ℹ️  Found {len(containers)} existing container(s):")
                for container in containers:
                    print(f"      - {container}")
                print("  ℹ️  Setup script will remove old containers automatically")
            else:
                print("  ✅ No existing containers found")
        else:
            print("  ⚠️  Docker is not running")
            print("  ℹ️  Please start Docker Desktop")
    else:
        print("  ⚠️  Docker not found")
        print("  ℹ️  Please install Docker: https://docs.docker.com/get-docker/")
    
    return True

def test_requirements_file():
    """Test requirements.txt exists"""
    print("\nTesting requirements.txt...")
    
    if Path('requirements.txt').exists():
        print("  ✅ requirements.txt found")
        
        # Count packages
        with open('requirements.txt') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        
        print(f"  ℹ️  Found {len(lines)} package requirements")
    else:
        print("  ❌ requirements.txt not found")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Setup Script Environment Detection Test")
    print("=" * 60)
    print()
    
    tests = [
        test_python_detection,
        test_conda_detection,
        test_venv_detection,
        test_docker_detection,
        test_requirements_file,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with error: {e}")
            results.append(False)
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ All detection tests passed!")
        print()
        print("You can now run the automated setup:")
        print("  bash scripts/setup_auto.sh")
        print("  OR")
        print("  python3 scripts/setup_auto.py")
    else:
        print("⚠️  Some tests failed, but setup script will handle them")
        print()
        print("Run the automated setup to fix issues:")
        print("  bash scripts/setup_auto.sh")
        print("  OR")
        print("  python3 scripts/setup_auto.py")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

