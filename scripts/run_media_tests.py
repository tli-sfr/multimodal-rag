#!/usr/bin/env python3
"""Run media extraction tests to verify all libraries are working.

This script runs unit tests for all media types to ensure that text can be
extracted from them before sending to ingestion.
"""

import sys
from pathlib import Path
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_tests(test_type=None, verbose=True):
    """Run media extraction tests.
    
    Args:
        test_type: Specific test type to run (library, text, image, audio, video, scene)
                  If None, runs all tests
        verbose: Show detailed output
    """
    
    cmd = ["pytest", "tests/test_media_extraction.py"]
    
    if verbose:
        cmd.extend(["-v", "-s"])  # Verbose and show print statements
    
    # Add markers based on test type
    if test_type:
        if test_type == "library":
            cmd.extend(["-k", "TestLibraryAvailability"])
        elif test_type == "text":
            cmd.extend(["-k", "TestTextExtraction"])
        elif test_type == "image":
            cmd.extend(["-k", "TestImageExtraction"])
        elif test_type == "audio":
            cmd.extend(["-k", "TestAudioExtraction"])
        elif test_type == "video":
            cmd.extend(["-k", "TestVideoExtraction"])
        elif test_type == "scene":
            cmd.extend(["-k", "TestSceneDetection"])
        else:
            print(f"Unknown test type: {test_type}")
            print("Valid types: library, text, image, audio, video, scene")
            return 1
    
    # Run tests
    print("=" * 80)
    print("Running Media Extraction Tests")
    print("=" * 80)
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=project_root)
    
    return result.returncode


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run media extraction tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python scripts/run_media_tests.py
  
  # Run only library availability tests (fast)
  python scripts/run_media_tests.py --type library
  
  # Run only text extraction tests
  python scripts/run_media_tests.py --type text
  
  # Run only image tests
  python scripts/run_media_tests.py --type image
  
  # Run only audio tests
  python scripts/run_media_tests.py --type audio
  
  # Run only video tests
  python scripts/run_media_tests.py --type video
  
  # Run only scene detection tests
  python scripts/run_media_tests.py --type scene
  
  # Run with minimal output
  python scripts/run_media_tests.py --quiet
        """
    )
    
    parser.add_argument(
        "--type",
        choices=["library", "text", "image", "audio", "video", "scene"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        verbose=not args.quiet
    )
    
    # Print summary
    print("\n" + "=" * 80)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 80)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

