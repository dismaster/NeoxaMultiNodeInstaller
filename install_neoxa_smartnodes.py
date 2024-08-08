import os
import subprocess
import urllib.request
import zipfile
import shutil
import getpass
from colorama import init, Fore, Style

init(autoreset=True)

# Define constants
neoxa_bin_dir = "/usr/local/bin"
neoxa_bin = os.path.join(neoxa_bin_dir, "neoxad")
neoxa_cli_bin = os.path.join(neoxa_bin_dir, "neoxa-cli")
neoxa_download_url = "https://github.com/NeoxaChain/Neoxa/releases/download/v5.1.1.4/neoxad-5.1.1.4-linux64.zip"
bootstrap_url = "https://downloads.neoxa.net/bootstrap.zip"
bootstrap_path = os.path.expanduser("~/bootstrap.zip")

# Configuration template with bind address
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
{bind_address}
"""

# Define donation address
donation_address = "GaRJcuLsqEcjbFjJVcenWG8EXsFmULdMwo"

def print_banner():
    banner = f"""
{Fore.MAGENTA}*********************************************
{Fore.MAGENTA}*          Script Developer: Ch3ckr         *
{Fore.MAGENTA}*                                           *
{Fore.MAGENTA}*             Donation Address              *
{Fore.MAGENTA}*   {donation_address.center(39)}   *
{Fore.MAGENTA}*********************************************
"""
    print(banner)

def print_thank_you():
    thank_you = f"""
{Fore.LIGHTMAGENTA_EX}*********************************************
{Fore.LIGHTMAGENTA_EX}*       Thank you for using this script!      *
{Fore.LIGHTMAGENTA_EX}*                                           *
{Fore.LIGHTMAGENTA_EX}*             Donation Address              *
{Fore.LIGHTMAGENTA_EX}*   {donation_address.center(39)}   *
{Fore.LIGHTMAGENTA_EX}*********************************************
"""
    print(thank_you)

def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result

def is_neoxad_installed():
    return os.path.exists(neoxa_bin) and os.path.exists(neoxa_cli_bin)

def install_neoxad():
    if is_neoxad_installed():
        print(f"{Fore.YELLOW}neoxad is already installed. Skipping installation.")
        return
    neoxa_zip = os.path.expanduser("~/neoxad.zip")
    print(f"{Fore.CYAN}Downloading neoxad from {neoxa_download_url} to {neoxa_zip}")
    urllib.request.urlretrieve(neoxa_download_url, neoxa_zip)
    with zipfile.ZipFile(neoxa_zip, 'r') as zip_ref:
        zip_ref.extractall(neoxa_bin_dir)
    os.remove(neoxa_zip)
    print(f"{Fore.GREEN}neoxad installed successfully")

def download_bootstrap():
    print(f"{Fore.CYAN}Downloading bootstrap from {bootstrap_url} to {bootstrap_path}")
    urllib.request.urlretrieve(bootstrap_url, bootstrap_path)
    print(f"{Fore.GREEN}Downloaded bootstrap to {bootstrap_path}")

def check_and_download_bootstrap():
    if os.path.exists(bootstrap_path):
        remote_file_info = urllib.request.urlopen(bootstrap_url)
        remote_file_size = int(remote_file_info.info()["Content-Length"])
        local_file_size = os.path.getsize(bootstrap_path)
        if remote_file_size != local_file_size:
            print(f"{Fore.CYAN}Remote bootstrap file size has changed, downloading the new version.")
            download_bootstrap()
        else:
            print(f"{Fore.GREEN}Local bootstrap file is up to date.")
    else:
        download_bootstrap()

def extract_bootstrap(temp_dir):
    print(f"{Fore.CYAN}Extracting bootstrap to {temp_dir}")
    with zipfile.ZipFile(bootstrap_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    print(f"{Fore.GREEN}Bootstrap extraction complete")

def create_data_dir(data_dir):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"{Fore.GREEN}Created directory: {data_dir}")
    else:
        print(f"{Fore.YELLOW}Directory already exists: {data_dir}")

def write_config(data_dir, rpcuser, rpcpassword, smartnodeblsprivkey, externalip, bind_address):
    config_path = os.path.join(data_dir, "neoxa.conf")
    config_content = neoxa_conf_template.format(
        rpcuser=rpcuser,
        rpcpassword=rpcpassword,
        smartnodeblsprivkey=smartnodeblsprivkey,
        externalip=externalip,
        bind_address=bind_address
    )
    with open(config_path, "w") as config_file:
        config_file.write(config_content)
    print(f"{Fore.GREEN}Wrote config to: {config_path}")

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
    print(f"{Fore.GREEN}Created bash script: {script_path}")
    return script_path

def add_crontab_entry(script_path):
    user = getpass.getuser()
    cron_command = f"@reboot {script_path} start\n"
    subprocess.run(f'(crontab -u {user} -l; echo "{cron_command}") | crontab -u {user} -', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"{Fore.GREEN}Added crontab entry for {script_path}")

def start_smartnode(data_dir):
    command = [neoxa_bin, "-datadir=" + data_dir]
    subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"{Fore.GREEN}Started Neoxa smartnode")

def get_input(prompt):
    return input(prompt).strip()

def prompt_for_natural_config():
    use_nat = get_input(f"{Fore.CYAN}Are you using NAT? (yes/no): ").strip().lower()
    if use_nat == 'yes':
        ip_type = get_input(f"{Fore.CYAN}Do you use IPv6 or IPv4? (ipv4/ipv6): ").strip().lower()
        if ip_type == 'ipv6':
            bind_address = f"bind=[{get_input(Fore.CYAN + 'Enter your IPv6 address: ', 'BIND_ADDRESS')]}]:8788"
        else:
            bind_address = f"bind={get_input(Fore.CYAN + 'Enter your IPv4 address: ', 'BIND_ADDRESS')}:8788"
    else:
        bind_address = ''
    return bind_address

def setup_node(node_number):
    data_dir = os.path.join(os.path.expanduser("~"), f"neoxa_node_{node_number}")
    bind_address = prompt_for_natural_config()

    print(f"{Fore.CYAN}Setting up Neoxa node {node_number}")

    rpcuser = get_input(f"{Fore.CYAN}Enter RPC user: ")
    rpcpassword = get_input(f"{Fore.CYAN}Enter RPC password: ")
    smartnodeblsprivkey = get_input(f"{Fore.CYAN}Enter smartnode BLS private key: ")
    externalip = get_input(f"{Fore.CYAN}Enter external IP: ")

    create_data_dir(data_dir)
    write_config(data_dir, rpcuser, rpcpassword, smartnodeblsprivkey, externalip, bind_address)
    script_path = create_bash_script(os.path.expanduser("~"), node_number, data_dir)
    add_crontab_entry(script_path)
    start_smartnode(data_dir)

def main():
    print_banner()
    install_neoxad()
    check_and_download_bootstrap()
    extract_bootstrap(temp_dir=os.path.expanduser("~"))
    print("All required components installed and configured.")
    print_thank_you()

if __name__ == "__main__":
    main()
