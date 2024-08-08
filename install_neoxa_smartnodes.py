import os
import subprocess
import urllib.request
import zipfile
import shutil
import getpass
import threading
import psutil
from colorama import init, Fore, Style

init(autoreset=True)

neoxa_bin_dir = "/usr/local/bin"
neoxa_bin = os.path.join(neoxa_bin_dir, "neoxad")
neoxa_cli_bin = os.path.join(neoxa_bin_dir, "neoxa-cli")
neoxa_download_url = "https://github.com/dismaster/NeoxaMultiNodeInstaller/main/install_neoxa_smartnodes.py"
bootstrap_url = "https://downloads.neoxa.net/bootstrap.zip"
bootstrap_path = "/tmp/bootstrap.zip"
neoxa_conf_template = """
rpcuser={rpcuser}
rpcpassword={rpcpassword}
rpcport=9494
rpcallowip=127.0.0.1
server=1
daemon=1
listen=1
smartnodeblsprivkey={smartnodeblsprivkey}
externalip={externalip}
"""

donation_address = "GaRJcuLsqEcjbFjJVcenWG8EXsFmULdMwo"

def print_banner():
    banner = f"""
{Fore.MAGENTA}*********************************************
{Fore.MAGENTA}*{Fore.LIGHTMAGENTA_EX}           Script Developer: Ch3ckr          {Fore.MAGENTA}*
{Fore.MAGENTA}*                                             *
{Fore.MAGENTA}*{Fore.LIGHTMAGENTA_EX}    Donation Address: {donation_address}    {Fore.MAGENTA}*
{Fore.MAGENTA}*********************************************
"""
    print(banner)

def print_thank_you():
    thank_you = f"""
{Fore.LIGHTMAGENTA_EX}*********************************************
{Fore.LIGHTMAGENTA_EX}*{Fore.MAGENTA}       Thank you for using this script!      {Fore.LIGHTMAGENTA_EX}*
{Fore.LIGHTMAGENTA_EX}*                                             *
{Fore.LIGHTMAGENTA_EX}*{Fore.MAGENTA}    Donation Address: {donation_address}    {Fore.LIGHTMAGENTA_EX}*
{Fore.LIGHTMAGENTA_EX}*********************************************
"""
    print(thank_you)

def is_neoxad_installed():
    return os.path.exists(neoxa_bin) and os.path.exists(neoxa_cli_bin)

def install_neoxad():
    if is_neoxad_installed():
        print(f"{Fore.YELLOW}neoxad is already installed. Skipping installation.")
        return
    neoxa_zip = "/tmp/neoxad.zip"
    print(f"Downloading neoxad from {neoxa_download_url} to {neoxa_zip}")
    urllib.request.urlretrieve(neoxa_download_url, neoxa_zip)
    with zipfile.ZipFile(neoxa_zip, 'r') as zip_ref:
        zip_ref.extractall(neoxa_bin_dir)
    os.remove(neoxa_zip)
    print("neoxad installed successfully")

def download_bootstrap():
    print(f"Downloading bootstrap from {bootstrap_url} to {bootstrap_path}")
    urllib.request.urlretrieve(bootstrap_url, bootstrap_path)
    print(f"Downloaded bootstrap to {bootstrap_path}")

def check_and_download_bootstrap():
    if os.path.exists(bootstrap_path):
        remote_file_info = urllib.request.urlopen(bootstrap_url)
        remote_file_size = int(remote_file_info.info()["Content-Length"])
        local_file_size = os.path.getsize(bootstrap_path)
        if remote_file_size != local_file_size:
            print("Remote bootstrap file size has changed, downloading the new version.")
            download_bootstrap()
        else:
            print("Local bootstrap file is up to date.")
    else:
        download_bootstrap()

def extract_bootstrap(temp_dir):
    print(f"Extracting bootstrap to {temp_dir}")
    with zipfile.ZipFile(bootstrap_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    print(f"Bootstrap extraction complete")

def create_data_dir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    else:
        print(f"Directory already exists: {data_dir}")

def write_config(data_dir, rpcuser, rpcpassword, smartnodeblsprivkey, externalip):
    config_path = os.path.join(data_dir, "neoxa.conf")
    config_content = neoxa_conf_template.format(
        rpcuser=rpcuser,
        rpcpassword=rpcpassword,
        smartnodeblsprivkey=smartnodeblsprivkey,
        externalip=externalip
    )
    with open(config_path, "w") as config_file:
        config_file.write(config_content)
    print(f"Wrote config to: {config_path}")

def copy_bootstrap(temp_dir, data_dir):
    for item in os.listdir(temp_dir):
        s = os.path.join(temp_dir, item)
        d = os.path.join(data_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    print(f"Copied bootstrap data to {data_dir}")

def create_bash_script(home_dir, node_number, data_dir):
    script_content = f"""#!/bin/bash

NEOXA_BIN="{neoxa_bin}"
NEOXA_CLI_BIN="{neoxa_cli_bin}"
DATA_DIR="{data_dir}"
SCREEN_NAME="neoxa_node_{node_number}"

start() {{
    screen -dmS ${{SCREEN_NAME}} ${{NEOXA_BIN}} -datadir=${{DATA_DIR}}
}}

stop() {{
    screen -S ${{SCREEN_NAME}} -X quit
}}

restart() {{
    stop
    start
}}

smartnode_status() {{
    ${{NEOXA_CLI_BIN}} -datadir=${{DATA_DIR}} smartnode status
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
    status)
        status
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|smartnode_status|status}}"
        exit 1
esac

exit 0
"""
    script_path = os.path.join(home_dir, f"neoxa_node_{node_number}.sh")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)
    os.chmod(script_path, 0o755)
    print(f"Created bash script: {script_path}")
    return script_path

def add_crontab_entry(script_path):
    user = getpass.getuser()
    cron_command = f"@reboot {script_path} start\n"
    subprocess.run(f'(crontab -u {user} -l; echo "{cron_command}") | crontab -u {user} -', shell=True, check=True)
    print(f"Added crontab entry for {script_path}")

def start_smartnode(data_dir):
    command = [neoxa_bin, "-datadir=" + data_dir]
    subprocess.run(command)
    print(f"Started Neoxa smartnode with data directory: {data_dir}")

def get_existing_nodes(home_dir):
    existing_nodes = []
    for item in os.listdir(home_dir):
        if item.startswith("neoxa_node_"):
            try:
                node_number = int(item.split("_")[-1])
                existing_nodes.append(node_number)
            except ValueError:
                continue
    return existing_nodes

def check_system_requirements():
    required_cores = 2
    required_memory = 4 * 1024 * 1024 * 1024  # 4GB in bytes
    required_disk_space = 60 * 1024 * 1024 * 1024  # 60GB in bytes

    available_cores = psutil.cpu_count(logical=False)
    available_memory = psutil.virtual_memory().available
    available_disk_space = psutil.disk_usage('/').free

    print(f"{Fore.CYAN}System resources available:")
    print(f"CPU Cores: {available_cores}")
    print(f"Memory: {available_memory / (1024 * 1024 * 1024):.2f} GB")
    print(f"Disk Space: {available_disk_space / (1024 * 1024 * 1024):.2f} GB")

    if available_cores < required_cores:
        print(f"{Fore.RED}Error: Not enough CPU cores available. Required: {required_cores}, Available: {available_cores}")
        return False
    if available_memory < required_memory:
        print(f"{Fore.RED}Error: Not enough memory available. Required: {required_memory / (1024 * 1024 * 1024):.2f} GB, Available: {available_memory / (1024 * 1024 * 1024):.2f} GB")
        return False
    if available_disk_space < required_disk_space:
        print(f"{Fore.RED}Error: Not enough disk space available. Required: {required_disk_space / (1024 * 1024 * 1024):.2f} GB, Available: {available_disk_space / (1024 * 1024 * 1024):.2f} GB")
        return False
    return True

def check_and_create_swap():
    swap = subprocess.run(['swapon', '--show'], capture_output=True, text=True)
    if swap.stdout:
        print(f"{Fore.GREEN}Swap is already enabled.")
    else:
        print(f"{Fore.YELLOW}No swap found. Creating a 4GB swap file...")
        subprocess.run(['sudo', 'fallocate', '-l', '4G', '/swapfile'])
        subprocess.run(['sudo', 'chmod', '600', '/swapfile'])
        subprocess.run(['sudo', 'mkswap', '/swapfile'])
        subprocess.run(['sudo', 'swapon', '/swapfile'])
        with open('/etc/fstab', 'a') as fstab:
            fstab.write('/swapfile none swap sw 0 0\n')
        print(f"{Fore.GREEN}Swap file created and enabled.")

def setup_smartnode(home_dir, node_number, rpcuser, rpcpassword, smartnodeblsprivkey, externalip, temp_bootstrap_dir):
    data_dir = os.path.join(home_dir, f"neoxa_node_{node_number}")
    create_data_dir(data_dir)
    write_config(data_dir, rpcuser, rpcpassword, smartnodeblsprivkey, externalip)
    copy_bootstrap(temp_bootstrap_dir, data_dir)
    script_path = create_bash_script(home_dir, node_number, data_dir)
    add_crontab_entry(script_path)
    start_smartnode(data_dir)

def main():
    print_banner()
    home_dir = os.path.expanduser("~")
    
    existing_nodes = get_existing_nodes(home_dir)
    num_existing_nodes = len(existing_nodes)
    if existing_nodes:
        next_node_number = max(existing_nodes) + 1
    else:
        next_node_number = 1

    num_smartnodes = int(input("Enter the number of additional smartnodes to install: "))
    
    if not check_system_requirements():
        print(f"{Fore.RED}System does not meet the requirements for installing additional nodes.")
        return

    check_and_create_swap()

    install_neoxad()
    check_and_download_bootstrap()
    
    temp_bootstrap_dir = os.path.join(home_dir, "temp_bootstrap")
    os.makedirs(temp_bootstrap_dir, exist_ok=True)
    extract_bootstrap(temp_bootstrap_dir)

    nodes_info = []
    for i in range(next_node_number, next_node_number + num_smartnodes):
        rpcuser = input(f"Enter RPC username for smartnode {i}: ")
        rpcpassword = input(f"Enter RPC password for smartnode {i}: ")
        smartnodeblsprivkey = input(f"Enter Smartnode BLS private key for smartnode {i}: ")
        externalip = input(f"Enter external IP (and port) for smartnode {i}: ")
        nodes_info.append((home_dir, i, rpcuser, rpcpassword, smartnodeblsprivkey, externalip, temp_bootstrap_dir))

    threads = []
    for node_info in nodes_info:
        thread = threading.Thread(target=setup_smartnode, args=node_info)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    shutil.rmtree(temp_bootstrap_dir)
    print("Removed temporary bootstrap directory")

    print_thank_you()

if __name__ == "__main__":
    main()
