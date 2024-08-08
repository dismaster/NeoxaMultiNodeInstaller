#!/bin/bash

# Variables
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/dismaster/NeoxaMultiNodeInstaller/main/install_neoxa_smartnodes.py"
SCRIPT_NAME="install_neoxa_smartnodes.py"
VENV_DIR="$HOME/neoxa_venv"

# Update package list and install prerequisites
echo "Updating package list and installing prerequisites..."
sudo apt-get update -y
sudo apt-get install -y wget curl git python3-venv

# Install Python if not installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Installing Python..."
    sudo apt-get install -y python3 python3-venv python3-pip
else
    echo "Python is already installed."
fi

# Ensure pip is installed and updated
if ! command -v pip3 &> /dev/null; then
    echo "pip is not installed. Installing pip..."
    sudo apt-get install -y python3-pip
else
    echo "pip is already installed. Upgrading pip..."
    sudo pip3 install --upgrade pip
fi

# Install screen if not installed
if ! command -v screen &> /dev/null; then
    echo "screen is not installed. Installing screen..."
    sudo apt-get install -y screen
else
    echo "screen is already installed."
fi

# Create a virtual environment
echo "Creating a virtual environment..."
python3 -m venv $VENV_DIR

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install required Python packages
echo "Installing required Python packages..."
pip install colorama psutil

# Download the Python script from GitHub
echo "Downloading the Python script from GitHub..."
wget -O $SCRIPT_NAME $PYTHON_SCRIPT_URL

# Run the Python script
echo "Running the Python script..."
python3 $SCRIPT_NAME

# Deactivate the virtual environment
deactivate

echo "Setup and execution completed."
