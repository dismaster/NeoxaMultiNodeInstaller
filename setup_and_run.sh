#!/bin/bash

# Define color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Define variables
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/dismaster/NeoxaMultiNodeInstaller/main/install_neoxa_smartnodes.py"
PYTHON_SCRIPT_NAME="install_neoxa_smartnodes.py"
REQUIRED_PACKAGES=("python3" "python3-pip" "curl" "screen")

# Function to install required packages
install_prerequisites() {
    echo -e "${CYAN}Updating package list and installing prerequisites...${NC}"
    sudo apt-get update -qq
    for pkg in "${REQUIRED_PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            echo -e "${CYAN}Installing $pkg...${NC}"
            sudo apt-get install -y $pkg > /dev/null
        fi
    done
}

# Function to download the Python script
download_python_script() {
    echo -e "${CYAN}Downloading the Python script...${NC}"
    curl -sSL $PYTHON_SCRIPT_URL -o $PYTHON_SCRIPT_NAME
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to download the Python script.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Python script downloaded successfully.${NC}"
}

# Function to check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
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
echo -e "${MAGENTA}************************************************************${NC}"
echo -e "${MAGENTA}* The setup is complete. To start the interactive Python script,${NC}"
echo -e "${MAGENTA}* use the following command:${NC}"
echo -e "${MAGENTA}*${NC}"
echo -e "${MAGENTA}* python3 $PYTHON_SCRIPT_NAME${NC}"
echo -e "${MAGENTA}*${NC}"
echo -e "${MAGENTA}* Follow the on-screen instructions to set up your Neoxa nodes.${NC}"
echo -e "${MAGENTA}************************************************************${NC}"
