#!/bin/bash
# Quick setup script for development

set -e

echo "=== Evohome Security Async - Development Setup ==="
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version)
echo "✓ Found: $python_version"
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Install package in development mode
echo "Installing package and dependencies..."
pip install -e ".[dev]"
echo "✓ Package installed in development mode"
echo

# Run tests
echo "Running tests..."
pytest tests/ -v
echo "✓ Tests passed"
echo

echo "=== Setup Complete ==="
echo
echo "To use the library:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Run the example: python example.py"
echo "  3. Or use in your own code:"
echo
echo "     from evohome_security_async import EvohomeSecurityClient"
echo
echo "For more information, see:"
echo "  - README.md for usage documentation"
echo "  - DEVELOPMENT.md for development guide"
echo "  - IMPROVEMENTS.md for comparison with original"
echo
