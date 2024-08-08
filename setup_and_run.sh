#!/bin/bash

# Define variables
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/dismaster/NeoxaMultiNodeInstaller/main/install_neoxa_smartnodes.py"
PYTHON_SCRIPT_NAME="install_neoxa_smartnodes.py"
REQUIRED_PACKAGES=("python3" "python3-pip" "curl" "screen")

# Function to install required packages
install_prerequisites() {
    echo "Updating package list and installing prerequisites..."
    sudo apt-get update
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            sudo apt-get install -y $pkg
        fi
    done
}

# Function to download the Python script
download_python_script() {
    echo "Downloading the Python script..."
    curl -sSL $PYTHON_SCRIPT_URL -o $PYTHON_SCRIPT_NAME
    if [ $? -ne 0 ]; then
        echo "Failed to download the Python script."
        exit 1
    fi
    echo "Python script downloaded successfully."
}

# Function to check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 is not installed. Please install Python 3 and try again."
        exit 1
    fi
}

# Install prerequisites
install_prerequisites

# Download the Python script
download_python_script

# Check for Python 3
check_python

# Instructions to the user
echo "************************************************************"
echo "* The setup is complete. To start the interactive Python script,"
echo "* use the following command:"
echo "*"
echo "* python3 $PYTHON_SCRIPT_NAME"
echo "*"
echo "* Follow the on-screen instructions to set up your Neoxa nodes."
echo "************************************************************"
