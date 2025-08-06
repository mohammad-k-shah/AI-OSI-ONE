#!/usr/bin/env python3
"""
Development Setup Script

This script sets up the development environment for OSI ONE AGENT.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚀 Setting up OSI ONE AGENT development environment...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    commands = [
        ("pip install -r requirements.txt", "Installing core dependencies"),
        ("pip install -r requirements-dev.txt", "Installing development dependencies"),
        ("pip install -e .", "Installing package in development mode"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            print("❌ Setup failed. Please check the errors above.")
            sys.exit(1)
    
    # Create necessary directories
    directories = [
        "logs",
        "config/auth",
        "tests/unit",
        "tests/integration",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Development environment setup completed!")
    print("\nNext steps:")
    print("1. Configure your API tokens in config/auth/")
    print("2. Update configuration files in config/")
    print("3. Run tests: pytest")
    print("4. Start development: python src/main.py")


if __name__ == "__main__":
    main() 