#!/usr/bin/env python3
"""
Tailscale/Headscale Dynamic Inventory Script
=============================================
Discovers machines connected to your Tailscale or Headscale network.

Supported backends:
  - Tailscale (via API)
  - Headscale (via API)
  - Local Tailscale CLI (tailscale status)

Requirements:
  pip install requests

Configuration (environment variables):
  For Tailscale API:
    TAILSCALE_API_KEY=tskey-api-xxx
    TAILSCALE_TAILNET=your-tailnet.ts.net  (or organization name)

  For Headscale API:
    HEADSCALE_URL=https://headscale.example.com
    HEADSCALE_API_KEY=your-api-key

  For local CLI (no auth needed):
    TAILSCALE_CLI=true

  Optional:
    TAILSCALE_INVENTORY_USE_FQDN=true  (use MagicDNS names)
    TAILSCALE_INVENTORY_TAG_PREFIX=ansible-  (filter by tag prefix)

Usage:
  # Using Tailscale API
  export TAILSCALE_API_KEY="tskey-api-xxx"
  export TAILSCALE_TAILNET="example.ts.net"
  ./tailscale_inventory.py --list

  # Using Headscale API
  export HEADSCALE_URL="https://headscale.example.com"
  export HEADSCALE_API_KEY="your-key"
  ./tailscale_inventory.py --list

  # Using local Tailscale CLI
  export TAILSCALE_CLI=true
  ./tailscale_inventory.py --list

  # With Ansible
  ansible-inventory -i inventories/dynamic/tailscale_inventory.py --list
  ansible-playbook -i inventories/dynamic/tailscale_inventory.py playbooks/provision.yml
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any, Optional

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def get_empty_inventory() -> dict:
    """Return empty inventory structure."""
    return {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "hosts": [],
            "children": ["ungrouped", "tailscale"]
        },
        "ungrouped": {
            "hosts": []
        },
        "tailscale": {
            "hosts": [],
            "children": []
        }
    }


def get_tailscale_api_inventory() -> dict:
    """Fetch inventory from Tailscale API."""
    if not HAS_REQUESTS:
        sys.stderr.write("Error: 'requests' module required. Install with: pip install requests\n")
        return get_empty_inventory()

    api_key = os.environ.get('TAILSCALE_API_KEY')
    tailnet = os.environ.get('TAILSCALE_TAILNET')

    if not api_key or not tailnet:
        sys.stderr.write("Error: TAILSCALE_API_KEY and TAILSCALE_TAILNET required\n")
        return get_empty_inventory()

    use_fqdn = os.environ.get('TAILSCALE_INVENTORY_USE_FQDN', 'false').lower() == 'true'
    tag_prefix = os.environ.get('TAILSCALE_INVENTORY_TAG_PREFIX', '')

    inventory = get_empty_inventory()

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }

        url = f'https://api.tailscale.com/api/v2/tailnet/{tailnet}/devices'
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        devices = response.json().get('devices', [])

        for device in devices:
            # Skip offline devices optionally
            # if not device.get('online', False):
            #     continue

            hostname = device.get('hostname', device.get('name', ''))
            if not hostname:
                continue

            # Use FQDN if configured
            if use_fqdn:
                fqdn = device.get('name', hostname)
                if '.' in fqdn:
                    hostname = fqdn

            # Get IP addresses
            addresses = device.get('addresses', [])
            ipv4 = next((ip for ip in addresses if '.' in ip), None)
            ipv6 = next((ip for ip in addresses if ':' in ip), None)

            # Build host variables
            hostvars = {
                'ansible_host': ipv4 or ipv6 or hostname,
                'tailscale_id': device.get('id'),
                'tailscale_name': device.get('name'),
                'tailscale_hostname': device.get('hostname'),
                'tailscale_ipv4': ipv4,
                'tailscale_ipv6': ipv6,
                'tailscale_os': device.get('os', 'unknown'),
                'tailscale_online': device.get('online', False),
                'tailscale_authorized': device.get('authorized', False),
                'tailscale_user': device.get('user', ''),
                'tailscale_created': device.get('created', ''),
                'tailscale_last_seen': device.get('lastSeen', ''),
            }

            # Determine ansible_user based on OS
            os_type = device.get('os', '').lower()
            if 'linux' in os_type or 'ubuntu' in os_type or 'debian' in os_type:
                hostvars['ansible_user'] = 'root'
            elif 'macos' in os_type or 'darwin' in os_type:
                hostvars['ansible_user'] = os.environ.get('USER', 'admin')

            # Add to main groups
            inventory['all']['hosts'].append(hostname)
            inventory['tailscale']['hosts'].append(hostname)
            inventory['_meta']['hostvars'][hostname] = hostvars

            # Group by online status
            status_group = 'online' if device.get('online') else 'offline'
            if status_group not in inventory:
                inventory[status_group] = {'hosts': [], 'children': []}
                inventory['tailscale']['children'].append(status_group)
            inventory[status_group]['hosts'].append(hostname)

            # Group by OS
            os_name = device.get('os', 'unknown').lower().replace(' ', '_')
            os_group = f'os_{os_name}'
            if os_group not in inventory:
                inventory[os_group] = {'hosts': [], 'children': []}
            inventory[os_group]['hosts'].append(hostname)

            # Group by tags
            tags = device.get('tags', [])
            for tag in tags:
                # Remove 'tag:' prefix if present
                tag_name = tag.replace('tag:', '')

                # Filter by prefix if configured
                if tag_prefix and not tag_name.startswith(tag_prefix):
                    continue

                # Clean tag name for group
                tag_group = f'tag_{tag_name}'.replace('-', '_').replace(':', '_')
                if tag_group not in inventory:
                    inventory[tag_group] = {'hosts': [], 'children': []}
                inventory[tag_group]['hosts'].append(hostname)

            # Group by user/owner
            user = device.get('user', '')
            if user:
                user_group = f"user_{user.split('@')[0].replace('.', '_').replace('-', '_')}"
                if user_group not in inventory:
                    inventory[user_group] = {'hosts': [], 'children': []}
                inventory[user_group]['hosts'].append(hostname)

        return inventory

    except requests.RequestException as e:
        sys.stderr.write(f"Error: Failed to fetch from Tailscale API: {e}\n")
        return get_empty_inventory()


def get_headscale_api_inventory() -> dict:
    """Fetch inventory from Headscale API."""
    if not HAS_REQUESTS:
        sys.stderr.write("Error: 'requests' module required. Install with: pip install requests\n")
        return get_empty_inventory()

    url = os.environ.get('HEADSCALE_URL', '').rstrip('/')
    api_key = os.environ.get('HEADSCALE_API_KEY')

    if not url or not api_key:
        sys.stderr.write("Error: HEADSCALE_URL and HEADSCALE_API_KEY required\n")
        return get_empty_inventory()

    use_fqdn = os.environ.get('TAILSCALE_INVENTORY_USE_FQDN', 'false').lower() == 'true'
    tag_prefix = os.environ.get('TAILSCALE_INVENTORY_TAG_PREFIX', '')

    inventory = get_empty_inventory()

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }

        # Fetch machines
        response = requests.get(f'{url}/api/v1/machine', headers=headers, timeout=30, verify=True)
        response.raise_for_status()

        machines = response.json().get('machines', [])

        for machine in machines:
            hostname = machine.get('givenName') or machine.get('name', '')
            if not hostname:
                continue

            # Get IP addresses
            ip_addresses = machine.get('ipAddresses', [])
            ipv4 = next((ip for ip in ip_addresses if '.' in ip), None)
            ipv6 = next((ip for ip in ip_addresses if ':' in ip), None)

            # Determine online status
            online = machine.get('online', False)

            # Build host variables
            hostvars = {
                'ansible_host': ipv4 or ipv6 or hostname,
                'headscale_id': machine.get('id'),
                'headscale_name': machine.get('name'),
                'headscale_given_name': machine.get('givenName'),
                'headscale_ipv4': ipv4,
                'headscale_ipv6': ipv6,
                'headscale_online': online,
                'headscale_user': machine.get('user', {}).get('name', ''),
                'headscale_namespace': machine.get('user', {}).get('name', ''),
                'headscale_created': machine.get('createdAt', ''),
                'headscale_last_seen': machine.get('lastSeen', ''),
                'headscale_expiry': machine.get('expiry', ''),
            }

            # Add to main groups
            inventory['all']['hosts'].append(hostname)
            inventory['tailscale']['hosts'].append(hostname)
            inventory['_meta']['hostvars'][hostname] = hostvars

            # Group by online status
            status_group = 'online' if online else 'offline'
            if status_group not in inventory:
                inventory[status_group] = {'hosts': [], 'children': []}
                inventory['tailscale']['children'].append(status_group)
            inventory[status_group]['hosts'].append(hostname)

            # Group by namespace/user
            namespace = machine.get('user', {}).get('name', 'default')
            ns_group = f'namespace_{namespace}'.replace('-', '_')
            if ns_group not in inventory:
                inventory[ns_group] = {'hosts': [], 'children': []}
            inventory[ns_group]['hosts'].append(hostname)

            # Group by forced tags
            forced_tags = machine.get('forcedTags', [])
            for tag in forced_tags:
                tag_name = tag.replace('tag:', '')
                if tag_prefix and not tag_name.startswith(tag_prefix):
                    continue
                tag_group = f'tag_{tag_name}'.replace('-', '_').replace(':', '_')
                if tag_group not in inventory:
                    inventory[tag_group] = {'hosts': [], 'children': []}
                inventory[tag_group]['hosts'].append(hostname)

            # Group by valid tags
            valid_tags = machine.get('validTags', [])
            for tag in valid_tags:
                tag_name = tag.replace('tag:', '')
                if tag_prefix and not tag_name.startswith(tag_prefix):
                    continue
                tag_group = f'tag_{tag_name}'.replace('-', '_').replace(':', '_')
                if tag_group not in inventory:
                    inventory[tag_group] = {'hosts': [], 'children': []}
                if hostname not in inventory[tag_group]['hosts']:
                    inventory[tag_group]['hosts'].append(hostname)

        return inventory

    except requests.RequestException as e:
        sys.stderr.write(f"Error: Failed to fetch from Headscale API: {e}\n")
        return get_empty_inventory()


def get_tailscale_cli_inventory() -> dict:
    """Fetch inventory from local Tailscale CLI."""
    inventory = get_empty_inventory()

    try:
        # Run tailscale status --json
        result = subprocess.run(
            ['tailscale', 'status', '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            sys.stderr.write(f"Error: tailscale status failed: {result.stderr}\n")
            return inventory

        status = json.loads(result.stdout)

        # Get self info
        self_node = status.get('Self', {})
        peers = status.get('Peer', {})

        # Process self
        if self_node:
            hostname = self_node.get('HostName', 'self')
            addresses = self_node.get('TailscaleIPs', [])
            ipv4 = next((ip for ip in addresses if '.' in ip), None)

            if hostname:
                inventory['all']['hosts'].append(hostname)
                inventory['tailscale']['hosts'].append(hostname)
                inventory['_meta']['hostvars'][hostname] = {
                    'ansible_host': ipv4 or hostname,
                    'tailscale_self': True,
                    'tailscale_ipv4': ipv4,
                    'tailscale_online': True,
                }

        # Process peers
        for peer_id, peer in peers.items():
            hostname = peer.get('HostName', '')
            if not hostname:
                continue

            addresses = peer.get('TailscaleIPs', [])
            ipv4 = next((ip for ip in addresses if '.' in ip), None)
            ipv6 = next((ip for ip in addresses if ':' in ip), None)

            online = peer.get('Online', False)
            os_type = peer.get('OS', 'unknown')

            hostvars = {
                'ansible_host': ipv4 or ipv6 or hostname,
                'tailscale_id': peer_id,
                'tailscale_hostname': hostname,
                'tailscale_ipv4': ipv4,
                'tailscale_ipv6': ipv6,
                'tailscale_online': online,
                'tailscale_os': os_type,
                'tailscale_rx_bytes': peer.get('RxBytes', 0),
                'tailscale_tx_bytes': peer.get('TxBytes', 0),
            }

            # Determine ansible_user
            os_lower = os_type.lower()
            if 'linux' in os_lower:
                hostvars['ansible_user'] = 'root'
            elif 'macos' in os_lower or 'darwin' in os_lower:
                hostvars['ansible_user'] = os.environ.get('USER', 'admin')

            inventory['all']['hosts'].append(hostname)
            inventory['tailscale']['hosts'].append(hostname)
            inventory['_meta']['hostvars'][hostname] = hostvars

            # Group by status
            status_group = 'online' if online else 'offline'
            if status_group not in inventory:
                inventory[status_group] = {'hosts': [], 'children': []}
                inventory['tailscale']['children'].append(status_group)
            inventory[status_group]['hosts'].append(hostname)

            # Group by OS
            os_group = f'os_{os_type.lower().replace(" ", "_")}'
            if os_group not in inventory:
                inventory[os_group] = {'hosts': [], 'children': []}
            inventory[os_group]['hosts'].append(hostname)

        return inventory

    except subprocess.TimeoutExpired:
        sys.stderr.write("Error: tailscale status timed out\n")
        return get_empty_inventory()
    except FileNotFoundError:
        sys.stderr.write("Error: tailscale CLI not found\n")
        return get_empty_inventory()
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Failed to parse tailscale status: {e}\n")
        return get_empty_inventory()


def get_inventory() -> dict:
    """Get inventory from appropriate source."""
    # Check for Headscale first
    if os.environ.get('HEADSCALE_URL') and os.environ.get('HEADSCALE_API_KEY'):
        return get_headscale_api_inventory()

    # Check for Tailscale API
    if os.environ.get('TAILSCALE_API_KEY') and os.environ.get('TAILSCALE_TAILNET'):
        return get_tailscale_api_inventory()

    # Check for CLI mode
    if os.environ.get('TAILSCALE_CLI', '').lower() == 'true':
        return get_tailscale_cli_inventory()

    # Return example inventory with instructions
    sys.stderr.write("""
No configuration found. Set one of the following:

For Tailscale API:
  export TAILSCALE_API_KEY="tskey-api-xxx"
  export TAILSCALE_TAILNET="your-tailnet.ts.net"

For Headscale API:
  export HEADSCALE_URL="https://headscale.example.com"
  export HEADSCALE_API_KEY="your-api-key"

For local Tailscale CLI:
  export TAILSCALE_CLI=true

""")
    return get_empty_inventory()


def get_host_vars(hostname: str) -> dict:
    """Get variables for a specific host."""
    inventory = get_inventory()
    return inventory.get('_meta', {}).get('hostvars', {}).get(hostname, {})


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Tailscale/Headscale Ansible Dynamic Inventory')
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
