#!/bin/bash

# Variables
PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/dismaster/NeoxaMultiNodeInstaller/main/install_neoxa_smartnodes.py"
SCRIPT_NAME="install_neoxa_smartnodes.py"

# Update package list and install prerequisites
echo -e "\e[96mUpdating package list and installing prerequisites...\e[0m"
sudo apt-get update -y > /dev/null
sudo apt-get install -y wget curl git python3-psutil python3-colorama screen > /dev/null

# Install Python if not installed
if ! command -v python3 &> /dev/null; then
    echo -e "\e[93mPython is not installed. Installing Python...\e[0m"
    sudo apt-get install -y python3 python3-venv python3-pip > /dev/null
else
    echo -e "\e[92mPython is already installed.\e[0m"
fi

# Download the Python script from GitHub
echo -e "\e[96mDownloading the Python script from GitHub...\e[0m"
wget -O $SCRIPT_NAME $PYTHON_SCRIPT_URL > /dev/null

# Run the Python script
echo -e "\e[96mRunning the Python script...\e[0m"
python3 $SCRIPT_NAME

echo -e "\e[92mSetup and execution completed.\e[0m"
