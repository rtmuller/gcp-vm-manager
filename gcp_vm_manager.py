#!/usr/bin/env python3
"""
GCP VM Manager
===========================
Advanced utility for managing and connecting to GCP VMs.
Provides a modern interactive interface with rich features for productivity.


Features:
- Interactive menu with real-time VM status
- Quick SSH access to VMs
- Common VM operations (start, stop, reset)
- View VM details and logs
- Transfer files to/from VMs
- Run commands on VMs remotely
- Project-wide operations
- SSH access to Cloud Run instances


Author: Rafael Muller
"""


import os
import sys
import json
import subprocess
import time
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
except ImportError:
    print("For best experience, install colorama: pip install colorama")
    # Fallback if colorama is not installed
    class ForeStub:
        def __init__(self):
            self.GREEN = ''
            self.RED = ''
            self.YELLOW = ''
            self.BLUE = ''
            self.CYAN = ''
            self.WHITE = ''
            self.MAGENTA = ''
            self.RESET = ''
    
    class StyleStub:
        def __init__(self):
            self.BRIGHT = ''
            self.DIM = ''
            self.NORMAL = ''
            self.RESET_ALL = ''
    
    Fore = ForeStub()
    Style = StyleStub()


try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    USE_RICH = True
    console = Console()
except ImportError:
    USE_RICH = False
    print("For best experience, install rich: pip install rich")

# Configuration file path
import os
# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

def load_config(config_file: str = None) -> Dict[str, Any]:
    """Load configuration from config.json file."""
    # Use the specified config file or the default
    config_path = config_file or CONFIG_FILE
    
    if not os.path.exists(config_path):
        # Create default config if it doesn't exist
        default_config = {
            "projects": {}
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config
    
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Error loading config file: {str(e)}{Fore.RESET}")
        return {"projects": {}}

def save_config(config: Dict[str, Any], config_file: str = None) -> None:
    """Save configuration to config.json file."""
    # Use the specified config file or the default
    config_path = config_file or CONFIG_FILE
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"{Fore.RED}Error saving config file: {str(e)}{Fore.RESET}")

def get_project_list(config_file: str = None) -> List[str]:
    """Get a list of all projects from the configuration."""
    config = load_config(config_file)
    return list(config.get("projects", {}).keys())

def run_command(command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def get_vm_status(project: str, vm_name: str, zone: str) -> str:
    """Get the status of a VM."""
    cmd = ["gcloud", "compute", "instances", "describe", vm_name,
           "--project", project, "--zone", zone,
           "--format", "json(status)"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code != 0:
        return "ERROR"
    
    try:
        data = json.loads(stdout)
        return data.get("status", "UNKNOWN")
    except:
        return "UNKNOWN"


def get_all_vm_statuses(project: str) -> Dict[str, str]:
    """Get statuses for all VMs in a project."""
    cmd = ["gcloud", "compute", "instances", "list",
           "--project", project,
           "--format", "json(name,status,zone)"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code != 0:
        print(f"{Fore.RED}Failed to get VM statuses: {stderr}{Fore.RESET}")
        return {}
    
    statuses = {}
    try:
        instances = json.loads(stdout)
        for instance in instances:
            name = instance.get("name", "")
            status = instance.get("status", "UNKNOWN")
            statuses[name] = status
            
            # Debug information to see all available VMs
            if "debug" in sys.argv:
                zone = instance.get("zone", "").split('/')[-1]
                print(f"Found VM: {name} in zone {zone} with status {status}")
    except Exception as e:
        print(f"{Fore.RED}Error parsing VM statuses: {str(e)}{Fore.RESET}")
        if "debug" in sys.argv:
            print(f"Raw output: {stdout}")
    
    return statuses


def print_header():
    """Print the application header."""
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
    print(f"           GCP VM MANAGER v1.1")
    print(f"{'=' * 60}{Style.RESET_ALL}")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{Fore.BLUE}Current time: {now}{Fore.RESET}")
    print()


def display_main_menu() -> int:
    """Display the main menu and let user select an option."""
    print_header()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Main Menu:{Style.RESET_ALL}")
    print(f"1) Manage Virtual Machines")
    print(f"2) Connect to Cloud Run Instances")
    print(f"3) Manage Projects")
    print(f"0) Exit")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-3): {Fore.RESET}")
            choice = int(choice)
            if 0 <= choice <= 3:
                return choice
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")


def display_projects(config_file: str = None) -> int:
    """Display a list of projects and let user select one."""
    print_header()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Select a project:{Style.RESET_ALL}")
    
    projects = get_project_list(config_file)
    if not projects:
        print(f"{Fore.YELLOW}No projects configured. Please add a project first.{Fore.RESET}")
        input("Press Enter to continue...")
        return 0
        
    for i, project in enumerate(projects, 1):
        env_type = "PRODUCTION" if "production" in project.lower() else "STAGING"
        color = Fore.RED if "production" in project.lower() else Fore.GREEN
        print(f"{i}) {project} {color}[{env_type}]{Fore.RESET}")
    
    print(f"0) Back to main menu")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-{len(projects)}): {Fore.RESET}")
            choice = int(choice)
            if 0 <= choice <= len(projects):
                return choice
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")


def display_vms(project: str, config_file: str = None) -> Tuple[Optional[Dict[str, Any]], int]:
    """Display VMs for a project and let user select one."""
    print_header()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Project: {project}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Loading VM statuses and information...{Fore.RESET}")
    
    # Always get VMs directly from GCP to ensure we have the complete list
    vms = []
    cmd = ["gcloud", "compute", "instances", "list",
           "--project", project,
           "--format", "json(name,zone,machineType,status,networkInterfaces[0].networkIP)"]
    
    code, stdout, stderr = run_command(cmd)
    
    # Debug information
    if "debug" in sys.argv:
        print(f"{Fore.BLUE}[DEBUG] Command: {' '.join(cmd)}{Fore.RESET}")
        print(f"{Fore.BLUE}[DEBUG] Exit code: {code}{Fore.RESET}")
        print(f"{Fore.BLUE}[DEBUG] stdout: {stdout}{Fore.RESET}")
        if stderr:
            print(f"{Fore.RED}[DEBUG] stderr: {stderr}{Fore.RESET}")
    
    if code != 0:
        print(f"{Fore.RED}Failed to get VM list: {stderr}{Fore.RESET}")
        print(f"{Fore.YELLOW}Troubleshooting tips:{Fore.RESET}")
        print("1. Verify you have the correct permissions for this project")
        print("2. Check if you're authenticated with the right account: gcloud auth list")
        print("3. Verify the project ID is correct")
        print("4. Try running the command manually: gcloud compute instances list --project " + project)
        input("Press Enter to return to project selection...")
        return None, 0
    
    try:
        instances = json.loads(stdout)
        if not instances:
            print(f"{Fore.YELLOW}No VMs found in this project.{Fore.RESET}")
            print(f"{Fore.YELLOW}Troubleshooting tips:{Fore.RESET}")
            print("1. Verify the project ID is correct")
            print("2. Check if you're looking at the right project")
            print("3. Try running: gcloud compute instances list --project " + project)
            input("Press Enter to return to project selection...")
            return None, 0
            
        statuses = {}
        # Load configuration to check for stored VM descriptions
        config = load_config(config_file)
        project_config = config.get("projects", {}).get(project, {})
        configured_vms = project_config.get("vms", [])
        
        for instance in instances:
            name = instance.get("name", "")
            zone_path = instance.get("zone", "")
            zone = zone_path.split('/')[-1] if zone_path else "Unknown"
            region = zone[:-2] if zone and len(zone) > 2 else "Unknown"  # Extract region from zone
            machine_type = instance.get("machineType", "").split('/')[-1] if instance.get("machineType") else "Unknown"
            status = instance.get("status", "UNKNOWN")
            
            # Map regions to more friendly names
            region_display = region
            if region.startswith("us-central"):
                region_display = "US Central"
            elif region.startswith("us-west"):
                region_display = "US West"
            elif region.startswith("us-east"):
                region_display = "US East"
            elif region.startswith("europe"):
                region_display = "Europe"
            elif region.startswith("asia"):
                region_display = "Asia"
            
            # Check if this VM matches one in our configuration (for descriptions)
            description = f"{machine_type} instance"
            for vm_info in configured_vms:
                if vm_info.get("name") == name and vm_info.get("zone") == zone:
                    description = vm_info.get("description", description)
                    break
            
            # Store the VM information
            vms.append({
                "name": name,
                "zone": zone,
                "region": region_display,
                "status": status,
                "description": description
            })
            statuses[name] = status
            
            # Also store this VM in the configuration if it's not already there
            vm_exists = False
            for vm_info in configured_vms:
                if vm_info.get("name") == name and vm_info.get("zone") == zone:
                    vm_exists = True
                    break
            
            if not vm_exists:
                configured_vms.append({
                    "name": name,
                    "zone": zone,
                    "region": region_display,
                    "description": description
                })
            
            # Debug information for each VM
            if "debug" in sys.argv:
                print(f"{Fore.BLUE}[DEBUG] Found VM: {name} in zone {zone} with status {status}{Fore.RESET}")
        
        # Save the updated configuration
        if project_config.get("vms") != configured_vms:
            project_config["vms"] = configured_vms
            config["projects"][project] = project_config
            save_config(config, config_file)
        
        # Sort VMs by name
        vms.sort(key=lambda x: x["name"])
        
    except Exception as e:
        print(f"{Fore.RED}Error parsing VM list: {str(e)}{Fore.RESET}")
        if "debug" in sys.argv:
            print(f"{Fore.RED}[DEBUG] Raw output: {stdout}{Fore.RESET}")
            import traceback
            traceback.print_exc()
        input("Press Enter to return to project selection...")
        return None, 0
    
    print_header()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Project: {project}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Select a VM:{Fore.RESET}")
    
    if not vms:
        print(f"{Fore.RED}No VMs found in this project.{Fore.RESET}")
        input("Press Enter to return to project selection...")
        return None, 0
    
    # Display VM table
    if USE_RICH:
        table = Table(title=f"VMs in {project}")
        table.add_column("#", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Region", style="yellow")
        table.add_column("Zone", style="blue")
        table.add_column("Status", style="magenta")
        table.add_column("Description")
        
        for i, vm in enumerate(vms, 1):
            name = vm["name"]
            status = vm["status"]
            status_color = "[green]" if status == "RUNNING" else "[red]" if status == "STOPPED" or status == "TERMINATED" else "[yellow]"
            
            table.add_row(
                str(i),
                name,
                vm.get("region", "Unknown"),
                vm.get("zone", "Unknown"),
                f"{status_color}{status}[/]",
                vm.get("description", "")
            )
        
        console.print(table)
    else:
        # Fallback for when rich is not installed
        print(f"{'#':<3} {'Name':<60} {'Region':<15} {'Zone':<20} {'Status':<10} {'Description'}")
        print("-" * 120)
        
        for i, vm in enumerate(vms, 1):
            name = vm["name"]
            status = vm["status"]
            status_color = Fore.GREEN if status == "RUNNING" else Fore.RED if status == "STOPPED" or status == "TERMINATED" else Fore.YELLOW
            
            print(f"{i:<3} {name:<60} {vm.get('region', 'Unknown'):<15} {vm.get('zone', 'Unknown'):<20} "
                  f"{status_color}{status:<10}{Fore.RESET} {vm.get('description', '')}")
    
    print(f"0) Back to project selection")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-{len(vms)}): {Fore.RESET}")
            choice = int(choice)
            if 0 <= choice <= len(vms):
                if choice == 0:
                    return None, 0
                return vms[choice-1], choice
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")


def vm_action_menu(project: str, vm: Dict[str, Any]) -> int:
    """Display actions for a selected VM."""
    vm_name = vm["name"]
    zone = vm["zone"]
    
    while True:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}Project: {project}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}VM: {vm_name} ({zone}){Style.RESET_ALL}")
        
        # Get current VM status
        status = get_vm_status(project, vm_name, zone)
        if status == "RUNNING":
            status_text = f"{Fore.GREEN}{status}{Fore.RESET}"
        elif status == "TERMINATED" or status == "STOPPED":
            status_text = f"{Fore.RED}{status}{Fore.RESET}"
        else:
            status_text = f"{Fore.YELLOW}{status}{Fore.RESET}"
        
        print(f"Status: {status_text}")
        print()
        
        print(f"{Fore.CYAN}Select an action:{Fore.RESET}")
        print(f"1) SSH into VM")
        
        if status == "RUNNING":
            print(f"2) Stop VM")
            print(f"3) Reset VM")
        elif status == "TERMINATED" or status == "STOPPED":
            print(f"2) Start VM")
            print(f"3) [Disabled] Reset VM")
        else:
            print(f"2) [Disabled] Stop VM")
            print(f"3) [Disabled] Reset VM")
        
        print(f"4) View VM details")
        print(f"5) View VM logs")
        print(f"6) Upload file to VM")
        print(f"7) Download file from VM")
        print(f"8) Run command on VM")
        print(f"0) Back to VM selection")
        
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-8): {Fore.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return 0
            elif choice == 1:
                ssh_to_vm(project, vm_name, zone)
            elif choice == 2:
                if status == "RUNNING":
                    stop_vm(project, vm_name, zone)
                elif status == "TERMINATED" or status == "STOPPED":
                    start_vm(project, vm_name, zone)
                else:
                    print(f"{Fore.RED}Cannot perform this action while VM is in {status} state.{Fore.RESET}")
                    input("Press Enter to continue...")
            elif choice == 3:
                if status == "RUNNING":
                    reset_vm(project, vm_name, zone)
                else:
                    print(f"{Fore.RED}Cannot reset VM while it's in {status} state.{Fore.RESET}")
                    input("Press Enter to continue...")
            elif choice == 4:
                view_vm_details(project, vm_name, zone)
            elif choice == 5:
                view_vm_logs(project, vm_name, zone)
            elif choice == 6:
                upload_file_to_vm(project, vm_name, zone)
            elif choice == 7:
                download_file_from_vm(project, vm_name, zone)
            elif choice == 8:
                run_command_on_vm(project, vm_name, zone)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
                input("Press Enter to continue...")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")
            input("Press Enter to continue...")


def ssh_to_vm(project: str, vm_name: str, zone: str):
    """SSH into a VM."""
    print(f"{Fore.CYAN}Connecting to {vm_name}...{Fore.RESET}")
    cmd = ["gcloud", "compute", "ssh", "--zone", zone, vm_name, 
           "--tunnel-through-iap", "--project", project]
    
    # For SSH, we don't capture output, just run the command directly
    subprocess.run(cmd)


def start_vm(project: str, vm_name: str, zone: str):
    """Start a VM."""
    print(f"{Fore.YELLOW}Starting {vm_name}...{Fore.RESET}")
    cmd = ["gcloud", "compute", "instances", "start", vm_name,
           "--project", project, "--zone", zone]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        print(f"{Fore.GREEN}VM started successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to start VM: {stderr}{Fore.RESET}")
    
    input("Press Enter to continue...")


def stop_vm(project: str, vm_name: str, zone: str):
    """Stop a VM."""
    print(f"{Fore.YELLOW}Stopping {vm_name}...{Fore.RESET}")
    cmd = ["gcloud", "compute", "instances", "stop", vm_name,
           "--project", project, "--zone", zone]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        print(f"{Fore.GREEN}VM stopped successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to stop VM: {stderr}{Fore.RESET}")
    
    input("Press Enter to continue...")


def reset_vm(project: str, vm_name: str, zone: str):
    """Reset a VM."""
    print(f"{Fore.YELLOW}Resetting {vm_name}...{Fore.RESET}")
    cmd = ["gcloud", "compute", "instances", "reset", vm_name,
           "--project", project, "--zone", zone]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        print(f"{Fore.GREEN}VM reset successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to reset VM: {stderr}{Fore.RESET}")
    
    input("Press Enter to continue...")


def view_vm_details(project: str, vm_name: str, zone: str):
    """View detailed information about a VM."""
    print(f"{Fore.YELLOW}Loading VM details...{Fore.RESET}")
    cmd = ["gcloud", "compute", "instances", "describe", vm_name,
           "--project", project, "--zone", zone,
           "--format", "json"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        try:
            details = json.loads(stdout)
            
            if USE_RICH:
                console.print(details, highlight=True)
            else:
                # Format JSON for readability
                details_str = json.dumps(details, indent=2)
                print(details_str)
        except:
            print(f"{Fore.RED}Failed to parse VM details.{Fore.RESET}")
            print(stdout)
    else:
        print(f"{Fore.RED}Failed to get VM details: {stderr}{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def view_vm_logs(project: str, vm_name: str, zone: str):
    """View logs from a VM."""
    print(f"{Fore.YELLOW}Loading VM logs...{Fore.RESET}")
    cmd = ["gcloud", "compute", "instances", "get-serial-port-output", vm_name,
           "--project", project, "--zone", zone]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        if USE_RICH:
            # Create a panel with scrollable content
            panel = Panel(stdout, title=f"Logs for {vm_name}", width=120, height=30)
            console.print(panel)
        else:
            print(stdout)
    else:
        print(f"{Fore.RED}Failed to get VM logs: {stderr}{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def upload_file_to_vm(project: str, vm_name: str, zone: str):
    """Upload a file to the VM."""
    print(f"{Fore.CYAN}Upload a file to {vm_name}{Fore.RESET}")
    
    local_path = input(f"Enter local file path: ")
    if not os.path.exists(local_path):
        print(f"{Fore.RED}File not found: {local_path}{Fore.RESET}")
        input("Press Enter to continue...")
        return
    
    remote_path = input(f"Enter remote path (default: ~/): ")
    if not remote_path:
        remote_path = "~/"
    
    print(f"{Fore.YELLOW}Uploading {local_path} to {vm_name}:{remote_path}...{Fore.RESET}")
    
    cmd = ["gcloud", "compute", "scp", local_path, 
           f"{vm_name}:{remote_path}", 
           "--project", project, "--zone", zone,
           "--tunnel-through-iap"]
    
    code, stdout, stderr = run_command(cmd, capture_output=False)
    
    if code == 0:
        print(f"{Fore.GREEN}File uploaded successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to upload file.{Fore.RESET}")
    
    input("Press Enter to continue...")


def download_file_from_vm(project: str, vm_name: str, zone: str):
    """Download a file from the VM."""
    print(f"{Fore.CYAN}Download a file from {vm_name}{Fore.RESET}")
    
    remote_path = input(f"Enter remote file path: ")
    local_path = input(f"Enter local path (default: ./): ")
    if not local_path:
        local_path = "./"
    
    print(f"{Fore.YELLOW}Downloading {vm_name}:{remote_path} to {local_path}...{Fore.RESET}")
    
    cmd = ["gcloud", "compute", "scp", 
           f"{vm_name}:{remote_path}", local_path,
           "--project", project, "--zone", zone,
           "--tunnel-through-iap"]
    
    code, stdout, stderr = run_command(cmd, capture_output=False)
    
    if code == 0:
        print(f"{Fore.GREEN}File downloaded successfully.{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to download file.{Fore.RESET}")
    
    input("Press Enter to continue...")


def run_command_on_vm(project: str, vm_name: str, zone: str):
    """Run a command on the VM."""
    print(f"{Fore.CYAN}Run a command on {vm_name}{Fore.RESET}")
    
    command = input(f"Enter command to run: ")
    if not command:
        print(f"{Fore.RED}No command entered.{Fore.RESET}")
        input("Press Enter to continue...")
        return
    
    print(f"{Fore.YELLOW}Running command on {vm_name}: {command}{Fore.RESET}")
    
    cmd = ["gcloud", "compute", "ssh", vm_name,
           "--project", project, "--zone", zone,
           "--tunnel-through-iap",
           "--command", command]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        print(f"{Fore.GREEN}Command executed successfully.{Fore.RESET}")
        print(f"\nOutput:\n{stdout}")
        if stderr:
            print(f"\nErrors:\n{Fore.RED}{stderr}{Fore.RESET}")
    else:
        print(f"{Fore.RED}Failed to execute command: {stderr}{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def get_cloud_run_services(project: str) -> List[Dict[str, Any]]:
    """Get all Cloud Run services for a project."""
    print(f"{Fore.BLUE}Loading Cloud Run services...{Fore.RESET}")
    cmd = ["gcloud", "run", "services", "list",
           "--project", project,
           "--format", "json"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code != 0:
        print(f"{Fore.RED}Failed to get Cloud Run services: {stderr}{Fore.RESET}")
        return []
    
    try:
        services = json.loads(stdout)
        return services
    except:
        print(f"{Fore.RED}Failed to parse Cloud Run services.{Fore.RESET}")
        return []


def display_cloud_run_services(project: str) -> Tuple[Optional[Dict[str, Any]], int]:
    """Display Cloud Run services for a project and let user select one."""
    print_header()
    print(f"{Fore.YELLOW}{Style.BRIGHT}Project: {project}{Style.RESET_ALL}")
    
    services = get_cloud_run_services(project)
    if not services:
        print(f"{Fore.RED}No Cloud Run services found in this project.{Fore.RESET}")
        input("Press Enter to return to project selection...")
        return None, 0
    
    print(f"{Fore.CYAN}Select a Cloud Run service:{Fore.RESET}")
    
    # Display services table
    if USE_RICH:
        table = Table(title=f"Cloud Run Services in {project}")
        table.add_column("#", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Region", style="yellow")
        table.add_column("URL", style="blue")
        table.add_column("Status", style="magenta")
        
        for i, service in enumerate(services, 1):
            name = service.get("metadata", {}).get("name", "Unknown")
            region = service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location", "Unknown")
            url = service.get("status", {}).get("url", "Unknown")
            status = "Ready" if service.get("status", {}).get("conditions", [{}])[0].get("status", "Unknown") == "True" else "Not Ready"
            status_color = "[green]" if status == "Ready" else "[red]"
            
            table.add_row(
                str(i),
                name,
                region,
                url,
                f"{status_color}{status}[/]"
            )
        
        console.print(table)
    else:
        # Fallback for when rich is not installed
        print(f"{'#':<3} {'Name':<40} {'Region':<15} {'URL':<50} {'Status':<10}")
        print("-" * 120)
        
        for i, service in enumerate(services, 1):
            name = service.get("metadata", {}).get("name", "Unknown")
            region = service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location", "Unknown")
            url = service.get("status", {}).get("url", "Unknown")
            status = "Ready" if service.get("status", {}).get("conditions", [{}])[0].get("status", "Unknown") == "True" else "Not Ready"
            status_color = Fore.GREEN if status == "Ready" else Fore.RED
            
            print(f"{i:<3} {name:<40} {region:<15} {url:<50} "
                  f"{status_color}{status:<10}{Fore.RESET}")
    
    print(f"0) Back to project selection")
    
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-{len(services)}): {Fore.RESET}")
            choice = int(choice)
            if 0 <= choice <= len(services):
                if choice == 0:
                    return None, 0
                return services[choice-1], choice
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")


def cloud_run_action_menu(project: str, service: Dict[str, Any]) -> int:
    """Display actions for a selected Cloud Run service."""
    service_name = service.get("metadata", {}).get("name", "Unknown")
    region = service.get("metadata", {}).get("labels", {}).get("cloud.googleapis.com/location", "Unknown")
    
    while True:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}Project: {project}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{Style.BRIGHT}Cloud Run Service: {service_name} ({region}){Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Select an action:{Fore.RESET}")
        print(f"1) SSH into Cloud Run instance")
        print(f"2) View service details")
        print(f"3) View service logs")
        print(f"0) Back to service selection")
        
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-3): {Fore.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return 0
            elif choice == 1:
                ssh_to_cloud_run(project, service_name, region)
            elif choice == 2:
                view_cloud_run_details(project, service_name, region)
            elif choice == 3:
                view_cloud_run_logs(project, service_name, region)
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
                input("Press Enter to continue...")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")
            input("Press Enter to continue...")


def ssh_to_cloud_run(project: str, service_name: str, region: str):
    """SSH into a Cloud Run instance."""
    print(f"{Fore.CYAN}Connecting to Cloud Run service {service_name}...{Fore.RESET}")
    
    # Ask if user wants debug mode
    debug_mode = input(f"{Fore.YELLOW}Enable debug mode? (y/N): {Fore.RESET}")
    debug_mode = debug_mode.lower() == 'y'
    
    if debug_mode:
        print(f"{Fore.BLUE}Debug mode enabled. Additional logs will be displayed.{Fore.RESET}")
    
    # First, check if the gcloud CLI version supports Cloud Run SSH
    version_cmd = ["gcloud", "--version"]
    code, stdout, stderr = run_command(version_cmd)
    
    if code != 0:
        print(f"{Fore.RED}Failed to get gcloud version: {stderr}{Fore.RESET}")
        input("Press Enter to continue...")
        return
    
    if debug_mode:
        print(f"{Fore.BLUE}[DEBUG] gcloud version info:{Fore.RESET}")
        print(stdout)
    
    # Check service details first
    print(f"{Fore.YELLOW}Checking service {service_name} details...{Fore.RESET}")
    cmd = ["gcloud", "run", "services", "describe", service_name,
           "--project", project, "--region", region,
           "--format", "json"]
    
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"{Fore.RED}Failed to get Cloud Run service details: {stderr}{Fore.RESET}")
        input("Press Enter to continue...")
        return
    
    if debug_mode:
        print(f"{Fore.BLUE}[DEBUG] Service details:{Fore.RESET}")
        try:
            details = json.loads(stdout)
            details_str = json.dumps(details, indent=2)
            print(details_str)
        except:
            print(stdout)
    
    # Get running instances/revisions
    print(f"{Fore.YELLOW}Checking active revisions for {service_name}...{Fore.RESET}")
    revisions_cmd = ["gcloud", "run", "revisions", "list",
                     "--service", service_name,
                     "--project", project, "--region", region,
                     "--format", "json"]
    
    code, stdout, stderr = run_command(revisions_cmd)
    
    if code != 0:
        print(f"{Fore.RED}Failed to get Cloud Run revisions: {stderr}{Fore.RESET}")
        input("Press Enter to continue...")
        return
    
    if debug_mode:
        print(f"{Fore.BLUE}[DEBUG] Revisions:{Fore.RESET}")
        try:
            revisions = json.loads(stdout)
            revisions_str = json.dumps(revisions, indent=2)
            print(revisions_str)
        except:
            print(stdout)
    
    # Show connection options
    print(f"\n{Fore.CYAN}Select a connection method:{Fore.RESET}")
    print(f"1) Try direct SSH (requires Cloud Run SSH enabled)")
    print(f"2) Use exec method (interactive shell)")
    print(f"3) Use debug container (advanced)")
    
    try:
        connection_choice = input(f"\n{Fore.CYAN}Enter your choice (1-3): {Fore.RESET}")
        connection_choice = int(connection_choice)
        
        if connection_choice == 1:
            # Try direct SSH method
            try_direct_ssh(project, service_name, region, debug_mode)
        elif connection_choice == 2:
            # Use exec method
            use_exec_method(project, service_name, region, debug_mode)
        elif connection_choice == 3:
            # Use debug container
            use_debug_container(project, service_name, region, debug_mode)
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
    except ValueError:
        print(f"{Fore.RED}Please enter a number.{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def try_direct_ssh(project: str, service_name: str, region: str, debug_mode: bool):
    """Try to use the built-in SSH feature of Cloud Run."""
    try:
        # Prepare the SSH command
        ssh_cmd = ["gcloud", "run", "services", "ssh", service_name,
                   "--project", project, "--region", region]
        
        # Add verbose flag if debug mode is enabled
        if debug_mode:
            ssh_cmd.append("--verbosity=debug")
        
        print(f"{Fore.YELLOW}Initiating SSH connection to Cloud Run service...{Fore.RESET}")
        if debug_mode:
            print(f"{Fore.BLUE}[DEBUG] Running command: {' '.join(ssh_cmd)}{Fore.RESET}")
        
        # For SSH, we don't capture output, just run the command directly
        result = subprocess.run(ssh_cmd, capture_output=debug_mode, text=True)
        
        if debug_mode and result.returncode != 0:
            print(f"{Fore.RED}[DEBUG] SSH command failed with code {result.returncode}{Fore.RESET}")
            print(f"{Fore.RED}[DEBUG] Error output:{Fore.RESET}")
            print(result.stderr)
            
            # Check if it's the "Invalid choice: 'ssh'" error
            if "Invalid choice: 'ssh'" in result.stderr:
                print(f"{Fore.YELLOW}The 'ssh' subcommand is not available in your gcloud version.{Fore.RESET}")
                print(f"{Fore.YELLOW}Please consider using one of the alternative connection methods.{Fore.RESET}")
        
    except Exception as e:
        print(f"{Fore.RED}Error connecting to Cloud Run instance: {str(e)}{Fore.RESET}")
        
        if debug_mode:
            import traceback
            print(f"{Fore.RED}[DEBUG] Full exception traceback:{Fore.RESET}")
            traceback.print_exc()
    
    # Provide troubleshooting tips if running in debug mode
    if debug_mode:
        print(f"\n{Fore.YELLOW}Troubleshooting tips for direct SSH:{Fore.RESET}")
        print(f"1. Ensure you have gcloud SDK version 428.0.0 or higher")
        print(f"2. Try updating with: gcloud components update")
        print(f"3. Verify the service has instances running")
        print(f"4. Check that you have the right IAM permissions")
        print(f"5. For more information, see: https://cloud.google.com/run/docs/debugging/ssh")


def use_exec_method(project: str, service_name: str, region: str, debug_mode: bool):
    """Use the exec method to get interactive shell access to a Cloud Run instance."""
    print(f"{Fore.YELLOW}Connecting to {service_name} using exec method...{Fore.RESET}")
    
    # First, get the latest revision
    revisions_cmd = ["gcloud", "run", "revisions", "list",
                     "--service", service_name,
                     "--project", project, "--region", region,
                     "--format", "json"]
    
    code, stdout, stderr = run_command(revisions_cmd)
    if code != 0 or not stdout:
        print(f"{Fore.RED}Failed to get revisions: {stderr}{Fore.RESET}")
        return
    
    try:
        revisions = json.loads(stdout)
        if not revisions:
            print(f"{Fore.RED}No revisions found for this service.{Fore.RESET}")
            return
        
        # Get the latest active revision
        active_revisions = [r for r in revisions if r.get("status", {}).get("conditions", [{}])[0].get("status") == "True"]
        if not active_revisions:
            print(f"{Fore.RED}No active revisions found. The service might not be running.{Fore.RESET}")
            return
        
        latest_revision = active_revisions[0]["metadata"]["name"]
        
        if debug_mode:
            print(f"{Fore.BLUE}[DEBUG] Using revision: {latest_revision}{Fore.RESET}")
        
        # Use Cloud Run Exec to connect to the container
        print(f"{Fore.GREEN}Connecting to revision {latest_revision}...{Fore.RESET}")
        
        # Get instance ID (for newer version of gcloud that support direct exec)
        print(f"{Fore.BLUE}Trying to get instances for direct connection...{Fore.RESET}")
        
        # Try multiple approaches for connecting to Cloud Run
        
        # Approach 1: Try using 'gcloud beta run services proxy'
        print(f"{Fore.YELLOW}Attempting to connect using proxy method...{Fore.RESET}")
        print(f"{Fore.YELLOW}This will open a local port connected to your Cloud Run service.{Fore.RESET}")
        
        print(f"\n{Fore.CYAN}Instructions for connecting:{Fore.RESET}")
        print(f"1. In a new terminal, after the proxy starts, connect using: curl http://localhost:8080")
        print(f"2. To execute a shell command, try: curl -X POST http://localhost:8080/debug/shell -d 'cmd=ls'")
        print(f"3. Press Ctrl+C in this terminal when done to stop the proxy")
        
        confirm = input(f"\n{Fore.CYAN}Start proxy connection? (y/N): {Fore.RESET}")
        if confirm.lower() != 'y':
            return
            
        # Run the proxy command
        proxy_cmd = ["gcloud", "beta", "run", "services", "proxy", service_name,
                   "--project", project, "--region", region, 
                   "--port", "8080"]
        
        if debug_mode:
            print(f"{Fore.BLUE}[DEBUG] Running command: {' '.join(proxy_cmd)}{Fore.RESET}")
        
        # Run the command directly - this will block until Ctrl+C
        try:
            subprocess.run(proxy_cmd)
        except KeyboardInterrupt:
            print(f"\n{Fore.GREEN}Proxy connection terminated.{Fore.RESET}")
    
    except Exception as e:
        print(f"{Fore.RED}Error using exec method: {str(e)}{Fore.RESET}")
        
        if debug_mode:
            import traceback
            print(f"{Fore.RED}[DEBUG] Full exception traceback:{Fore.RESET}")
            traceback.print_exc()


def use_debug_container(project: str, service_name: str, region: str, debug_mode: bool):
    """Connect to a Cloud Run instance via a debug container approach."""
    print(f"{Fore.YELLOW}Connecting using debug container method...{Fore.RESET}")
    
    # Check if the service is accepting connections
    print(f"{Fore.BLUE}Checking service URL...{Fore.RESET}")
    cmd = ["gcloud", "run", "services", "describe", service_name,
           "--project", project, "--region", region,
           "--format", "json(status.url)"]
    
    code, stdout, stderr = run_command(cmd)
    if code != 0:
        print(f"{Fore.RED}Failed to get service URL: {stderr}{Fore.RESET}")
        return
    
    try:
        url_data = json.loads(stdout)
        service_url = url_data.get("status", {}).get("url")
        
        if not service_url:
            print(f"{Fore.RED}Could not get service URL.{Fore.RESET}")
            return
        
        if debug_mode:
            print(f"{Fore.BLUE}[DEBUG] Service URL: {service_url}{Fore.RESET}")
        
        # Get an identity token for authentication
        print(f"{Fore.BLUE}Getting authentication token...{Fore.RESET}")
        token_cmd = ["gcloud", "auth", "print-identity-token", 
                     "--audiences", service_url]
        
        code, token, stderr = run_command(token_cmd)
        if code != 0:
            print(f"{Fore.RED}Failed to get authentication token: {stderr}{Fore.RESET}")
            return
        
        token = token.strip()
        
        if debug_mode:
            print(f"{Fore.BLUE}[DEBUG] Got token of length: {len(token)}{Fore.RESET}")
        
        # Offer options for accessing the container
        print(f"\n{Fore.CYAN}Debug container options:{Fore.RESET}")
        print(f"1) View environment variables")
        print(f"2) View file system (ls -la)")
        print(f"3) Show running processes (ps aux)")
        print(f"4) Check network connections (netstat -tuln)")
        print(f"5) Display memory usage (free -h)")
        print(f"6) Check disk space (df -h)")
        print(f"7) View system logs (tail /var/log/syslog)")
        print(f"8) Run custom command")
        print(f"9) Interactive mode (run multiple commands)")
        print(f"0) Cancel")
        
        try:
            debug_choice = input(f"\n{Fore.CYAN}Enter your choice (0-9): {Fore.RESET}")
            debug_choice = int(debug_choice)
            
            if debug_choice == 0:
                return
                
            # Define command based on choice
            command = ""
            if debug_choice == 1:
                method = "GET"
                endpoint = "/_debug/env"
            elif debug_choice == 2:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "ls -la"
            elif debug_choice == 3:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "ps aux"
            elif debug_choice == 4:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "netstat -tuln || ss -tuln"
            elif debug_choice == 5:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "free -h || cat /proc/meminfo"
            elif debug_choice == 6:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "df -h"
            elif debug_choice == 7:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = "tail /var/log/syslog 2>/dev/null || journalctl -n 50 2>/dev/null || echo 'No system logs available'"
            elif debug_choice == 8:
                method = "POST"
                endpoint = "/_debug/cmd"
                command = input(f"{Fore.CYAN}Enter command to run: {Fore.RESET}")
            elif debug_choice == 9:
                # Enter an interactive mode where user can run multiple commands
                print(f"{Fore.GREEN}Entering interactive mode. Type 'exit' to quit.{Fore.RESET}")
                
                while True:
                    cmd_input = input(f"{Fore.GREEN}cloud-run-debug> {Fore.RESET}")
                    if cmd_input.lower() == 'exit':
                        break
                    
                    # Execute the command
                    curl_cmd = ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
                               "-H", "Content-Type: application/json",
                               "-d", f'{{"command": "{cmd_input}"}}',
                               f"{service_url}/_debug/cmd"]
                    
                    if debug_mode:
                        masked_cmd = curl_cmd.copy()
                        masked_cmd[3] = "Authorization: Bearer [TOKEN]"
                        print(f"{Fore.BLUE}[DEBUG] Running: {' '.join(masked_cmd)}{Fore.RESET}")
                    
                    result = subprocess.run(curl_cmd, capture_output=True, text=True)
                    
                    # Format and print the output
                    try:
                        if result.stdout:
                            output = result.stdout.strip()
                            print()
                            print(output)
                            print()
                    except:
                        print(f"{Fore.RED}Error processing output{Fore.RESET}")
                
                return
            
            # Construct curl command to access debug endpoint
            if method == "GET":
                curl_cmd = ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
                           f"{service_url}{endpoint}"]
            else:
                curl_cmd = ["curl", "-s", "-H", f"Authorization: Bearer {token}", 
                           "-H", "Content-Type: application/json",
                           "-d", f'{{"command": "{command}"}}',
                           f"{service_url}{endpoint}"]
            
            if debug_mode:
                # Don't print the full token in debug output
                masked_cmd = curl_cmd.copy()
                if "-H" in masked_cmd:
                    auth_index = masked_cmd.index("-H") + 1
                    if auth_index < len(masked_cmd) and "Authorization: Bearer" in masked_cmd[auth_index]:
                        masked_cmd[auth_index] = "Authorization: Bearer [TOKEN]"
                print(f"{Fore.BLUE}[DEBUG] Running command: {' '.join(masked_cmd)}{Fore.RESET}")
            
            print(f"{Fore.GREEN}Executing command: {command if command else 'GET '+endpoint}{Fore.RESET}")
            result = subprocess.run(curl_cmd, capture_output=True, text=True)
            
            # Format and print the output
            try:
                if result.stdout:
                    output = result.stdout.strip()
                    
                    # Try to pretty print JSON if it's a JSON response
                    try:
                        json_data = json.loads(output)
                        output = json.dumps(json_data, indent=2)
                    except:
                        pass
                    
                    if USE_RICH:
                        title = f"Output of {command if command else endpoint}"
                        panel = Panel(output, title=title, width=120)
                        console.print(panel)
                    else:
                        print("\n" + "-" * 50)
                        print(output)
                        print("-" * 50 + "\n")
                
                if debug_mode and result.stderr:
                    print(f"{Fore.RED}[DEBUG] stderr: {result.stderr}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.RED}Error formatting output: {str(e)}{Fore.RESET}")
            
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")
        except Exception as e:
            print(f"{Fore.RED}Error in debug container method: {str(e)}{Fore.RESET}")
            
            if debug_mode:
                import traceback
                print(f"{Fore.RED}[DEBUG] Full exception traceback:{Fore.RESET}")
                traceback.print_exc()
    
    except Exception as e:
        print(f"{Fore.RED}Error using debug container: {str(e)}{Fore.RESET}")
        
        if debug_mode:
            import traceback
            print(f"{Fore.RED}[DEBUG] Full exception traceback:{Fore.RESET}")
            traceback.print_exc()


def view_cloud_run_details(project: str, service_name: str, region: str):
    """View detailed information about a Cloud Run service."""
    print(f"{Fore.YELLOW}Loading Cloud Run service details...{Fore.RESET}")
    cmd = ["gcloud", "run", "services", "describe", service_name,
           "--project", project, "--region", region,
           "--format", "json"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        try:
            details = json.loads(stdout)
            
            if USE_RICH:
                console.print(details, highlight=True)
            else:
                # Format JSON for readability
                details_str = json.dumps(details, indent=2)
                print(details_str)
        except:
            print(f"{Fore.RED}Failed to parse Cloud Run service details.{Fore.RESET}")
            print(stdout)
    else:
        print(f"{Fore.RED}Failed to get Cloud Run service details: {stderr}{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def view_cloud_run_logs(project: str, service_name: str, region: str):
    """View logs from a Cloud Run service."""
    print(f"{Fore.YELLOW}Loading Cloud Run service logs...{Fore.RESET}")
    cmd = ["gcloud", "logging", "read", 
           f"resource.type=cloud_run_revision AND resource.labels.service_name={service_name}",
           f"--project={project}", "--limit=100", "--format=json"]
    
    code, stdout, stderr = run_command(cmd)
    
    if code == 0:
        try:
            logs = json.loads(stdout)
            formatted_logs = ""
            
            for entry in logs:
                timestamp = entry.get("timestamp", "Unknown time")
                message = entry.get("textPayload", entry.get("jsonPayload", {}).get("message", "No message"))
                severity = entry.get("severity", "INFO")
                
                severity_color = {
                    "ERROR": Fore.RED,
                    "WARNING": Fore.YELLOW,
                    "INFO": Fore.GREEN,
                    "DEBUG": Fore.BLUE
                }.get(severity, Fore.WHITE)
                
                formatted_logs += f"{timestamp} {severity_color}[{severity}]{Fore.RESET} {message}\n\n"
            
            if USE_RICH:
                # Create a panel with scrollable content
                panel = Panel(formatted_logs or "No logs found", 
                              title=f"Logs for {service_name}", 
                              width=120, height=30)
                console.print(panel)
            else:
                print(formatted_logs or "No logs found")
        except Exception as e:
            print(f"{Fore.RED}Failed to parse Cloud Run logs: {str(e)}{Fore.RESET}")
            print(stdout)
    else:
        print(f"{Fore.RED}Failed to get Cloud Run logs: {stderr}{Fore.RESET}")
    
    input("\nPress Enter to continue...")


def manage_cloud_run(config_file: str):
    """Main flow for Cloud Run management."""
    while True:
        project_choice = display_projects(config_file)
        
        if project_choice == 0:
            return
        
        project = get_project_list(config_file)[project_choice - 1]
        
        while True:
            service, service_choice = display_cloud_run_services(project)
            if service_choice == 0:
                break
            
            result = cloud_run_action_menu(project, service)
            if result == 0:
                continue


def manage_vms(config_file: str):
    """Main flow for VM management."""
    while True:
        project_choice = display_projects(config_file)
        
        if project_choice == 0:
            return
        
        project = get_project_list(config_file)[project_choice - 1]
        
        while True:
            vm, vm_choice = display_vms(project, config_file)
            if vm_choice == 0:
                break
            
            vm_result = vm_action_menu(project, vm)
            if vm_result == 0:
                continue


def manage_projects(config: Dict[str, Any], config_file: str) -> None:
    """Manage projects in the configuration."""
    while True:
        print_header()
        print(f"{Fore.YELLOW}{Style.BRIGHT}Project Management{Style.RESET_ALL}")
        print(f"1) List configured projects")
        print(f"2) Add new project")
        print(f"3) Remove project")
        print(f"0) Back to main menu")
        
        try:
            choice = input(f"\n{Fore.CYAN}Enter your choice (0-3): {Fore.RESET}")
            choice = int(choice)
            
            if choice == 0:
                return
            elif choice == 1:
                projects = get_project_list(config_file)
                if not projects:
                    print(f"{Fore.YELLOW}No projects configured.{Fore.RESET}")
                else:
                    print(f"\n{Fore.GREEN}Configured projects:{Fore.RESET}")
                    for project in projects:
                        print(f"- {project}")
                input("\nPress Enter to continue...")
            elif choice == 2:
                project_name = input(f"{Fore.CYAN}Enter project name: {Fore.RESET}")
                if project_name:
                    if project_name in config["projects"]:
                        print(f"{Fore.RED}Project already exists.{Fore.RESET}")
                    else:
                        config["projects"][project_name] = {"vms": []}
                        save_config(config, config_file)
                        print(f"{Fore.GREEN}Project added successfully.{Fore.RESET}")
                input("\nPress Enter to continue...")
            elif choice == 3:
                projects = get_project_list(config_file)
                if not projects:
                    print(f"{Fore.YELLOW}No projects to remove.{Fore.RESET}")
                    input("\nPress Enter to continue...")
                    continue
                
                print(f"\n{Fore.GREEN}Select project to remove:{Fore.RESET}")
                for i, project in enumerate(projects, 1):
                    print(f"{i}) {project}")
                print(f"0) Cancel")
                
                try:
                    remove_choice = input(f"\n{Fore.CYAN}Enter your choice (0-{len(projects)}): {Fore.RESET}")
                    remove_choice = int(remove_choice)
                    
                    if 0 < remove_choice <= len(projects):
                        project_to_remove = projects[remove_choice - 1]
                        confirm = input(f"{Fore.YELLOW}Are you sure you want to remove {project_to_remove}? (y/N): {Fore.RESET}")
                        if confirm.lower() == 'y':
                            del config["projects"][project_to_remove]
                            save_config(config, config_file)
                            print(f"{Fore.GREEN}Project removed successfully.{Fore.RESET}")
                except ValueError:
                    print(f"{Fore.RED}Invalid choice.{Fore.RESET}")
                input("\nPress Enter to continue...")
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Fore.RESET}")
                input("\nPress Enter to continue...")
        except ValueError:
            print(f"{Fore.RED}Please enter a number.{Fore.RESET}")
            input("\nPress Enter to continue...")


def main():
    """Main application flow."""
    # Parse command line arguments
    args = parse_args()
    
    # Handle --no-color flag
    if args.no_color:
        global Fore
        global Style
        # Create stub classes for colorama if --no-color is used
        class ForeStub:
            def __init__(self):
                self.GREEN = ''
                self.RED = ''
                self.YELLOW = ''
                self.BLUE = ''
                self.CYAN = ''
                self.WHITE = ''
                self.MAGENTA = ''
                self.RESET = ''
        
        class StyleStub:
            def __init__(self):
                self.BRIGHT = ''
                self.DIM = ''
                self.NORMAL = ''
                self.RESET_ALL = ''
        
        Fore = ForeStub()
        Style = StyleStub()
    
    # Load configuration using the path from args
    config = load_config(args.config)
    
    # Display debug information if --debug flag is set
    if args.debug:
        print(f"{Fore.BLUE}Debug mode enabled{Fore.RESET}")
        print(f"Python version: {sys.version}")
        print(f"Operating system: {sys.platform}")
        print(f"Config file path: {args.config}")
        print()
    
    # Main loop
    try:
        while True:
            main_choice = display_main_menu()
            
            if main_choice == 0:
                print(f"{Fore.GREEN}Goodbye!{Fore.RESET}")
                sys.exit(0)
            elif main_choice == 1:
                manage_vms(args.config)
            elif main_choice == 2:
                manage_cloud_run(args.config)
            elif main_choice == 3:
                manage_projects(config, args.config)
    except KeyboardInterrupt:
        print(f"\n{Fore.GREEN}Goodbye!{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {str(e)}{Fore.RESET}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="GCP VM Manager")
    parser.add_argument('--version', action='version', version='1.1')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-color', action='store_true', help='Disable colored output')
    parser.add_argument('--config', type=str, help='Path to config file', default=CONFIG_FILE)
    return parser.parse_args()


if __name__ == "__main__":
    main() 