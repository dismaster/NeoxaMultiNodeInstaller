import os
import subprocess
import urllib.request
import zipfile
import shutil
import getpass
import threading
import psutil
import socket
import json
import re
from tqdm import tqdm
from colorama import init, Fore

init(autoreset=True)

bootstrap_url = "https://downloads.neoxa.net/bootstrap.zip"

user_home_dir = os.path.expanduser("~")
neoxa_bin_dir = os.path.join(user_home_dir, "neoxa")
neoxa_bin = os.path.join(neoxa_bin_dir, "neoxad")
neoxa_cli_bin = os.path.join(neoxa_bin_dir, "neoxa-cli")
neoxa_zip = os.path.join(user_home_dir, "neoxad.zip")
bootstrap_path = os.path.join(user_home_dir, "bootstrap.zip")
bootstrap_temp_dir = os.path.join(user_home_dir, "bootstrap_temp")

donation_address = "GaRJcuLsqEcjbFjJVcenWG8EXsFmULdMwo"

def print_banner():
    cpu_info = f"CPU: {psutil.cpu_count(logical=True)} cores"
    memory_info = f"Memory: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB"
    disk_info = f"Disk: {psutil.disk_usage('/').total / (1024 ** 3):.2f} GB"
    banner = f"""
{Fore.MAGENTA}#############################################
{Fore.MAGENTA}#          Script Developer: Ch3ckr         #
{Fore.MAGENTA}#############################################
{Fore.CYAN}               System Information           
{Fore.CYAN}         {cpu_info}                               
{Fore.CYAN}         {memory_info}                            
{Fore.CYAN}         {disk_info}                              
{Fore.MAGENTA}#############################################
{Fore.MAGENTA}#             Donation Address              #
{Fore.MAGENTA}#    {donation_address}     #
{Fore.MAGENTA}#############################################
"""
    print(banner)

def print_thank_you():
    thank_you = f"""
{Fore.MAGENTA}#############################################
{Fore.MAGENTA}#             Thanks and Goodbye            #
{Fore.MAGENTA}#          Script Developer: Ch3ckr         #
{Fore.MAGENTA}#############################################
{Fore.MAGENTA}#             Donation Address              #
{Fore.MAGENTA}#    {donation_address}     #
{Fore.MAGENTA}#############################################

"""
    print(thank_you)

def get_installed_neoxad_version():
    if not os.path.exists(neoxa_bin):
        return None

    try:
        result = subprocess.run([neoxa_bin, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        version_output = result.stdout.splitlines()[0]
        match = re.search(r"v(\d+\.\d+\.\d+\.\d+)", version_output)
        if match:
            return match.group(0)
        else:
            return "unknown"
    except Exception as e:
        return "unknown"

def get_latest_neoxad_version():
    try:
        response = urllib.request.urlopen("https://api.github.com/repos/NeoxaChain/Neoxa/releases/latest")
        latest_release = json.loads(response.read().decode())
        version = latest_release["tag_name"]
        download_url = next(asset["browser_download_url"] for asset in latest_release["assets"] if "linux64" in asset["name"])
        return version, download_url
    except Exception as e:
        return None, None

def install_neoxad():
    installed_version = get_installed_neoxad_version()
    latest_version, latest_download_url = get_latest_neoxad_version()

    if installed_version is None:
        print(f"{Fore.CYAN}Installing neoxad version {latest_version}...")
    elif installed_version == latest_version:
        return
    else:
        update_choice = input(f"{Fore.YELLOW}Do you want to update neoxad to version {latest_version}? (y/n): ").strip().lower()
        if update_choice != 'y':
            return
        else:
            print(f"{Fore.CYAN}Updating neoxad from {installed_version} to {latest_version}...")

    urllib.request.urlretrieve(latest_download_url, neoxa_zip)
    with zipfile.ZipFile(neoxa_zip, 'r') as zip_ref:
        zip_ref.extractall(neoxa_bin_dir)
    
    os.chmod(neoxa_bin, 0o755)
    os.chmod(neoxa_cli_bin, 0o755)
    
    os.remove(neoxa_zip)
    print(f"{Fore.GREEN}neoxad installed successfully")

def download_bootstrap():
    with urllib.request.urlopen(bootstrap_url) as response:
        total_size = int(response.info().get('Content-Length', 0))
        block_size = 8192
        with open(bootstrap_path, 'wb') as file, tqdm(
            desc=bootstrap_path,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in iter(lambda: response.read(block_size), b''):
                file.write(data)
                bar.update(len(data))

def check_and_download_bootstrap():
    if os.path.exists(bootstrap_path):
        remote_file_info = urllib.request.urlopen(bootstrap_url)
        remote_file_size = int(remote_file_info.info()["Content-Length"])
        local_file_size = os.path.getsize(bootstrap_path)
        if remote_file_size != local_file_size:
            download_bootstrap()
    else:
        download_bootstrap()

def extract_bootstrap():
    # Ensure the bootstrap_temp_dir exists before extraction
    if not os.path.exists(bootstrap_temp_dir):
        os.makedirs(bootstrap_temp_dir)
    
    if not os.listdir(bootstrap_temp_dir):
        with zipfile.ZipFile(bootstrap_path, 'r') as zip_ref:
            zip_ref.extractall(bootstrap_temp_dir)

def create_data_dir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

def list_ip_addresses():
    ip_addresses = []
    for interface in psutil.net_if_addrs().values():
        for snic in interface:
            if snic.family in (socket.AF_INET, socket.AF_INET6) and snic.address not in ('127.0.0.1', '::1'):
                ip_addresses.append(snic.address)
    return ip_addresses

def get_used_ip_addresses():
    used_ips = []
    existing_dirs = [d for d in os.listdir(user_home_dir) if d.startswith('neoxa_node_')]
    for directory in existing_dirs:
        config_path = os.path.join(user_home_dir, directory, "neoxa.conf")
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                for line in config_file:
                    if line.startswith("bind="):
                        ip = line.split('=')[1].split(':')[0].strip("[]")
                        used_ips.append(ip)
                        break
    return used_ips

def get_next_rpc_port():
    existing_ports = []
    existing_dirs = [d for d in os.listdir(user_home_dir) if d.startswith('neoxa_node_')]
    for directory in existing_dirs:
        config_path = os.path.join(user_home_dir, directory, "neoxa.conf")
        if os.path.exists(config_path):
            with open(config_path, 'r') as config_file:
                for line in config_file:
                    if line.startswith("rpcport="):
                        port = int(line.split('=')[1].strip())
                        existing_ports.append(port)
                        break
    if existing_ports:
        return max(existing_ports) + 1
    else:
        return 9494  # Start with the default port if no existing ports are found

def select_ip_address(ip_addresses, used_ips):
    normalized_used_ips = [ip.strip("[]") for ip in used_ips]
    available_ips = [ip for ip in ip_addresses if ip.strip("[]") not in normalized_used_ips]
    
    if not available_ips:
        print(f"{Fore.RED}No available IP addresses found.")
        return None

    print(f"{Fore.CYAN}Available IP addresses:")
    for index, ip in enumerate(available_ips, start=1):
        print(f"{Fore.CYAN}{index}. {ip}")

    selection = int(input(f"{Fore.CYAN}Select an IP address by number: ").strip())
    if 1 <= selection <= len(available_ips):
        return available_ips[selection - 1]
    else:
        print(f"{Fore.RED}Invalid selection.")
        return None

def write_config(data_dir, node_number, smartnodeblsprivkey, externalip, bind_address):
    rpcuser = f"node-{node_number}"
    rpcpassword = f"node-{node_number}"
    rpcport = get_next_rpc_port()
    rpcallowip = "127.0.0.1"

    if ":" in bind_address:
        bind = f"[{bind_address}]:8788"
    else:
        bind = f"{bind_address}:8788"

    config_content = f"""
rpcuser={rpcuser}
rpcpassword={rpcpassword}
rpcport={rpcport}
rpcallowip={rpcallowip}
server=1
listen=1
bind={bind}
smartnodeblsprivkey={smartnodeblsprivkey}
externalip={externalip}
"""
    config_path = os.path.join(data_dir, "neoxa.conf")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

def copy_bootstrap(data_dir):
    for item in os.listdir(bootstrap_temp_dir):
        s = os.path.join(bootstrap_temp_dir, item)
        d = os.path.join(data_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

def create_bash_script(home_dir, node_number, data_dir):
    script_content = f"""
#!/bin/bash

SCREEN_NAME="neoxa_node_{node_number}"
NEOXA_BIN="{neoxa_bin}"
NEOXA_CLI_BIN="{neoxa_cli_bin}"
DATA_DIR="{data_dir}"

start() {{
    screen -dmS ${{SCREEN_NAME}} ${{NEOXA_BIN}} -datadir=${{DATA_DIR}} -printtoconsole
}}

stop() {{
    screen -S ${{SCREEN_NAME}} -X quit
}}

restart() {{
    stop
    sleep 1
    start
}}

smartnode_status() {{
    ${{NEOXA_CLI_BIN}} -datadir=${{DATA_DIR}} smartnode status
}}

getblockchaininfo() {{
    ${{NEOXA_CLI_BIN}} -datadir=${{DATA_DIR}} getblockchaininfo
}}

getinfo() {{
    ${{NEOXA_CLI_BIN}} -datadir=${{DATA_DIR}} getinfo
}}

status() {{
    if screen -list | grep -q "${{SCREEN_NAME}}"; then
        echo "Node is running"
    else
        echo "Node is not running"
    fi
}}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    smartnode_status)
        smartnode_status
        ;;
    getblockchaininfo)
        getblockchaininfo
        ;;
    getinfo)
        getinfo
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|smartnode_status|getblockchaininfo|getinfo|status}}"
        exit 1
esac

exit 0
"""
    script_path = os.path.join(home_dir, f"neoxa_node_{node_number}.sh")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    os.chmod(script_path, 0o755)
    return script_path

def add_crontab_entry(script_path):
    user = getpass.getuser()
    cron_command = f"@reboot {script_path} start\n"
    subprocess.run(f'(crontab -u {user} -l; echo "{cron_command}") | crontab -u {user} -', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_smartnode(node_name, data_dir):
    command = ["screen", "-dmS", node_name, neoxa_bin, f"-datadir={data_dir}", "-printtoconsole"]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_next_node_number():
    existing_dirs = [d for d in os.listdir(user_home_dir) if d.startswith('neoxa_node_')]
    existing_numbers = [int(d.split('_')[-1]) for d in existing_dirs if d.split('_')[-1].isdigit()]
    if existing_numbers:
        return max(existing_numbers) + 1
    else:
        return 1

def main():
    print_banner()

    num_smartnodes = int(input("Amount of nodes: "))

    install_neoxad()
    check_and_download_bootstrap()
    extract_bootstrap()

    next_node_number = get_next_node_number()

    used_ips = get_used_ip_addresses()

    for i in range(next_node_number, next_node_number + num_smartnodes):
        print(f"\nConfiguring Node {i}")
        ip_addresses = list_ip_addresses()
        bind_address = select_ip_address(ip_addresses, used_ips)
        if not bind_address:
            continue

        smartnodeblsprivkey = input(f"Smartnode BLS private key for node {i}: ")
        externalip = input(f"External IP (include [] for IPv6) for node {i}: ")

        data_dir = os.path.join(user_home_dir, f"neoxa_node_{i}")
        create_data_dir(data_dir)
        write_config(data_dir, i, smartnodeblsprivkey, externalip, bind_address)
        copy_bootstrap(data_dir)
        script_path = create_bash_script(user_home_dir, i, data_dir)
        add_crontab_entry(script_path)

        start_smartnode(f"neoxa_node_{i}", data_dir)

    print_thank_you()

if __name__ == "__main__":
    main()
