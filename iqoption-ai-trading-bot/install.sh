#!/bin/bash

# IQ Option AI Trading Bot - Installation Script

echo "========================================"
echo "  IQ Option AI Trading Bot Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install TA-Lib dependency (for Ubuntu/Debian)
echo ""
echo "Checking TA-Lib dependencies..."
if [ "$(uname -s)" == "Linux" ]; then
    echo "Installing TA-Lib dependencies..."
    sudo apt-get update
    sudo apt-get install -y build-essential wget
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    sudo make install
    cd ..
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file
echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo ""
    echo "IMPORTANT: Edit .env file with your credentials:"
    echo "  - IQ Option email and password"
    echo "  - OpenAI API key (for LLM features)"
    echo ""
else
    echo ".env file already exists"
fi

# Create directories
echo ""
echo "Creating directories..."
mkdir -p logs
mkdir -p strategies
mkdir -p reports

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your credentials"
echo "  2. Activate virtual environment: source venv/bin/activate"
echo "  3. Run the bot: python main.py --demo"
echo ""
echo "For help: python main.py --help"
echo ""