#!/usr/bin/env python3
"""
Custom Dynamic Inventory Script
================================
Flexible inventory script that can pull hosts from multiple sources.

Supported sources:
  - JSON/YAML file
  - REST API endpoint
  - Database query
  - Environment variables

Usage:
  ./custom_inventory.py --list
  ./custom_inventory.py --host <hostname>
  ansible-inventory -i inventories/dynamic/custom_inventory.py --list
  ansible-playbook -i inventories/dynamic/custom_inventory.py playbooks/provision.yml

Configuration:
  Set ANSIBLE_INVENTORY_SOURCE environment variable to specify source type:
    - file:/path/to/inventory.json
    - http://api.example.com/inventory
    - env:PREFIX_  (reads PREFIX_HOST_* environment variables)

Examples:
  ANSIBLE_INVENTORY_SOURCE=file:./hosts.json ./custom_inventory.py --list
  ANSIBLE_INVENTORY_SOURCE=http://cmdb.example.com/api/hosts ./custom_inventory.py --list
"""

import argparse
import json
import os
import sys
from typing import Any

# Optional imports for extended functionality
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def get_empty_inventory() -> dict:
    """Return empty inventory structure."""
    return {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": [],
            "children": ["ungrouped"]
        },
        "ungrouped": {
            "hosts": []
        }
    }


def load_from_file(filepath: str) -> dict:
    """Load inventory from JSON or YAML file."""
    if not os.path.exists(filepath):
        sys.stderr.write(f"Error: File not found: {filepath}\n")
        return get_empty_inventory()

    with open(filepath, 'r') as f:
        content = f.read()

    # Try JSON first
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try YAML
    if HAS_YAML:
        try:
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                return data
        except yaml.YAMLError:
            pass

    sys.stderr.write(f"Error: Could not parse file as JSON or YAML: {filepath}\n")
    return get_empty_inventory()


def load_from_api(url: str) -> dict:
    """Load inventory from REST API endpoint."""
    if not HAS_REQUESTS:
        sys.stderr.write("Error: 'requests' module required for API source. Install with: pip install requests\n")
        return get_empty_inventory()

    try:
        headers = {}

        # Check for API token in environment
        api_token = os.environ.get('ANSIBLE_INVENTORY_API_TOKEN')
        if api_token:
            headers['Authorization'] = f'Bearer {api_token}'

        # Check for API key
        api_key = os.environ.get('ANSIBLE_INVENTORY_API_KEY')
        if api_key:
            headers['X-API-Key'] = api_key

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        sys.stderr.write(f"Error: Failed to fetch inventory from API: {e}\n")
        return get_empty_inventory()


def load_from_env(prefix: str) -> dict:
    """
    Load inventory from environment variables.

    Expected format:
      PREFIX_HOSTS=host1,host2,host3
      PREFIX_HOST_host1_IP=192.168.1.10
      PREFIX_HOST_host1_USER=ubuntu
      PREFIX_HOST_host1_GROUPS=webservers,production
      PREFIX_GROUP_webservers_HOSTS=host1,host2
    """
    inventory = get_empty_inventory()

    # Get host list
    hosts_var = os.environ.get(f'{prefix}HOSTS', '')
    if not hosts_var:
        return inventory

    hosts = [h.strip() for h in hosts_var.split(',') if h.strip()]

    for host in hosts:
        # Add to all hosts
        inventory['all']['hosts'].append(host)

        # Get host variables
        host_prefix = f'{prefix}HOST_{host}_'
        hostvars = {}

        for key, value in os.environ.items():
            if key.startswith(host_prefix):
                var_name = key[len(host_prefix):].lower()

                # Special handling for common variables
                if var_name == 'ip':
                    hostvars['ansible_host'] = value
                elif var_name == 'user':
                    hostvars['ansible_user'] = value
                elif var_name == 'port':
                    hostvars['ansible_port'] = int(value)
                elif var_name == 'groups':
                    # Handle group membership
                    for group in value.split(','):
                        group = group.strip()
                        if group and group not in inventory:
                            inventory[group] = {'hosts': [], 'children': []}
                        if group:
                            inventory[group]['hosts'].append(host)
                else:
                    hostvars[var_name] = value

        if hostvars:
            inventory['_meta']['hostvars'][host] = hostvars

    # Process group definitions
    for key, value in os.environ.items():
        if key.startswith(f'{prefix}GROUP_') and key.endswith('_HOSTS'):
            group = key[len(f'{prefix}GROUP_'):-6]
            if group not in inventory:
                inventory[group] = {'hosts': [], 'children': []}
            for host in value.split(','):
                host = host.strip()
                if host and host not in inventory[group]['hosts']:
                    inventory[group]['hosts'].append(host)

    return inventory


def load_from_netbox(url: str) -> dict:
    """
    Load inventory from NetBox DCIM/IPAM.

    Requires:
      - NETBOX_TOKEN environment variable
      - NetBox API URL
    """
    if not HAS_REQUESTS:
        sys.stderr.write("Error: 'requests' module required for NetBox. Install with: pip install requests\n")
        return get_empty_inventory()

    token = os.environ.get('NETBOX_TOKEN')
    if not token:
        sys.stderr.write("Error: NETBOX_TOKEN environment variable required\n")
        return get_empty_inventory()

    inventory = get_empty_inventory()

    try:
        headers = {
            'Authorization': f'Token {token}',
            'Accept': 'application/json'
        }

        # Fetch devices
        devices_url = f"{url.rstrip('/')}/api/dcim/devices/?status=active"
        response = requests.get(devices_url, headers=headers, timeout=30)
        response.raise_for_status()
        devices = response.json().get('results', [])

        for device in devices:
            hostname = device.get('name')
            if not hostname:
                continue

            inventory['all']['hosts'].append(hostname)

            hostvars = {
                'netbox_id': device.get('id'),
                'netbox_url': device.get('url'),
            }

            # Get primary IP
            primary_ip = device.get('primary_ip4') or device.get('primary_ip6')
            if primary_ip:
                ip_address = primary_ip.get('address', '').split('/')[0]
                if ip_address:
                    hostvars['ansible_host'] = ip_address

            # Get device type/role for grouping
            device_role = device.get('device_role', {}).get('slug', 'unknown')
            if device_role not in inventory:
                inventory[device_role] = {'hosts': [], 'children': []}
            inventory[device_role]['hosts'].append(hostname)

            # Get site for grouping
            site = device.get('site', {}).get('slug', 'unknown')
            site_group = f'site_{site}'
            if site_group not in inventory:
                inventory[site_group] = {'hosts': [], 'children': []}
            inventory[site_group]['hosts'].append(hostname)

            # Add custom fields
            custom_fields = device.get('custom_fields', {})
            for key, value in custom_fields.items():
                if value is not None:
                    hostvars[f'netbox_{key}'] = value

            inventory['_meta']['hostvars'][hostname] = hostvars

        return inventory

    except requests.RequestException as e:
        sys.stderr.write(f"Error: Failed to fetch from NetBox: {e}\n")
        return get_empty_inventory()


def get_inventory() -> dict:
    """Get inventory from configured source."""
    source = os.environ.get('ANSIBLE_INVENTORY_SOURCE', '')

    if not source:
        # Default: return example inventory
        return {
            "_meta": {
                "hostvars": {
                    "example-host": {
                        "ansible_host": "192.168.1.100",
                        "ansible_user": "ubuntu",
                        "environment": "development"
                    }
                }
            },
            "all": {
                "hosts": ["example-host"],
                "children": ["ungrouped", "development"]
            },
            "ungrouped": {
                "hosts": []
            },
            "development": {
                "hosts": ["example-host"]
            }
        }

    # Parse source type
    if source.startswith('file:'):
        filepath = source[5:]
        return load_from_file(filepath)

    elif source.startswith('http://') or source.startswith('https://'):
        return load_from_api(source)

    elif source.startswith('env:'):
        prefix = source[4:]
        return load_from_env(prefix)

    elif source.startswith('netbox:'):
        url = source[7:]
        return load_from_netbox(url)

    else:
        sys.stderr.write(f"Error: Unknown source type: {source}\n")
        sys.stderr.write("Supported: file:, http://, https://, env:, netbox:\n")
        return get_empty_inventory()


def get_host_vars(hostname: str) -> dict:
    """Get variables for a specific host."""
    inventory = get_inventory()
    return inventory.get('_meta', {}).get('hostvars', {}).get(hostname, {})


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Custom Ansible Dynamic Inventory')
    parser.add_argument('--list', action='store_true', help='List all hosts')
    parser.add_argument('--host', help='Get variables for a specific host')

    args = parser.parse_args()

    if args.list:
        inventory = get_inventory()
        print(json.dumps(inventory, indent=2))
    elif args.host:
        hostvars = get_host_vars(args.host)
        print(json.dumps(hostvars, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
