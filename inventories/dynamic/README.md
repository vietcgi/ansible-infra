# Dynamic Inventory

This directory contains dynamic inventory configurations for automatically discovering hosts from various cloud providers and infrastructure sources.

## Quick Start

```bash
# List hosts from AWS EC2
ansible-inventory -i inventories/dynamic/aws.aws_ec2.yml --list

# Run playbook against Hetzner Cloud
ansible-playbook -i inventories/dynamic/hcloud.yml playbooks/provision.yml

# Combine static and dynamic inventories
ansible-playbook -i inventories/production -i inventories/dynamic/aws.aws_ec2.yml playbooks/provision.yml
```

## Available Inventories

| File | Provider | Requirements |
|------|----------|--------------|
| `aws.aws_ec2.yml` | AWS EC2 | `pip install boto3`, `amazon.aws` collection |
| `hcloud.yml` | Hetzner Cloud | `pip install hcloud`, `hetzner.hcloud` collection |
| `digitalocean.yml` | DigitalOcean | `pip install requests`, `community.digitalocean` collection |
| `proxmox.proxmox.yml` | Proxmox VE | `pip install proxmoxer requests`, `community.proxmox` collection |
| `cloud.linode.yml` | Linode | `pip install linode_api4`, `community.general` collection (included) |
| `vultr.yml` | Vultr | `pip install requests`, `vultr.cloud` collection |
| `tailscale_inventory.py` | Tailscale/Headscale | `pip install requests` |
| `custom_inventory.py` | Custom sources | `pip install requests` (optional) |

**Note**: File names must match plugin requirements:
- AWS: `*.aws_ec2.yml`
- Proxmox: `*.proxmox.yml`
- Linode: `*.linode.yml`

## Configuration

### AWS EC2

```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option 2: AWS credentials file (~/.aws/credentials)
# Option 3: IAM instance role (when running on EC2)

# Install requirements
pip install boto3 botocore
ansible-galaxy collection install amazon.aws

# Test
ansible-inventory -i inventories/dynamic/aws.aws_ec2.yml --list
```

### Hetzner Cloud

```bash
export HCLOUD_TOKEN="your-api-token"

pip install hcloud
ansible-galaxy collection install hetzner.hcloud

ansible-inventory -i inventories/dynamic/hcloud.yml --list
```

### DigitalOcean

```bash
export DO_API_TOKEN="your-api-token"

pip install requests
ansible-galaxy collection install community.digitalocean

ansible-inventory -i inventories/dynamic/digitalocean.yml --list
```

### Proxmox VE

```bash
export PROXMOX_URL="https://pve.example.com:8006"
export PROXMOX_USER="ansible@pam"
export PROXMOX_PASSWORD="your-password"

# Or use API token (recommended)
export PROXMOX_TOKEN_ID="ansible@pam!ansible-token"
export PROXMOX_TOKEN_SECRET="your-token-secret"

pip install proxmoxer requests
ansible-galaxy collection install community.proxmox

ansible-inventory -i inventories/dynamic/proxmox.proxmox.yml --list
```

### Linode

```bash
export LINODE_ACCESS_TOKEN="your-api-token"

pip install linode_api4
# community.general is usually pre-installed

ansible-inventory -i inventories/dynamic/cloud.linode.yml --list
```

### Vultr

```bash
export VULTR_API_KEY="your-api-key"

pip install requests
ansible-galaxy collection install vultr.cloud

ansible-inventory -i inventories/dynamic/vultr.yml --list
```

### Tailscale / Headscale

```bash
# For Tailscale API
export TAILSCALE_API_KEY="tskey-api-xxx"
export TAILSCALE_TAILNET="your-tailnet.ts.net"

# For Headscale API
export HEADSCALE_URL="https://headscale.example.com"
export HEADSCALE_API_KEY="your-api-key"

# For local Tailscale CLI (no API key needed)
export TAILSCALE_CLI=true

pip install requests
ansible-inventory -i inventories/dynamic/tailscale_inventory.py --list
```

### Custom Inventory Script

```bash
# From JSON file
export ANSIBLE_INVENTORY_SOURCE="file:./hosts.json"

# From REST API
export ANSIBLE_INVENTORY_SOURCE="http://cmdb.example.com/api/hosts"
export ANSIBLE_INVENTORY_API_TOKEN="your-token"

# From NetBox
export ANSIBLE_INVENTORY_SOURCE="netbox:https://netbox.example.com"
export NETBOX_TOKEN="your-netbox-token"

# From environment variables
export ANSIBLE_INVENTORY_SOURCE="env:MYINFRA_"
export MYINFRA_HOSTS="web1,web2,db1"
export MYINFRA_HOST_web1_IP="192.168.1.10"
export MYINFRA_HOST_web1_USER="ubuntu"
export MYINFRA_HOST_web1_GROUPS="webservers,production"

ansible-inventory -i inventories/dynamic/custom_inventory.py --list
```

## Combining Inventories

You can combine multiple inventory sources:

```bash
# Static + AWS + Tailscale
ansible-playbook playbooks/provision.yml \
  -i inventories/production \
  -i inventories/dynamic/aws.aws_ec2.yml \
  -i inventories/dynamic/tailscale_inventory.py
```

Or create an inventory directory:

```bash
mkdir -p inventories/combined
ln -s ../production/hosts.yml inventories/combined/
ln -s ../dynamic/aws.aws_ec2.yml inventories/combined/
ln -s ../dynamic/hcloud.yml inventories/combined/

ansible-playbook -i inventories/combined playbooks/provision.yml
```

## Caching

All inventory plugins support caching to reduce API calls:

```yaml
# In inventory file
cache: true
cache_plugin: jsonfile
cache_connection: /tmp/ansible_cache
cache_timeout: 300  # 5 minutes
```

Clear cache:
```bash
rm -rf /tmp/ansible_*_cache
```

## Grouping

Dynamic inventories automatically create groups based on:

- **Cloud provider**: `aws_ec2`, `hcloud`, `digitalocean`, `proxmox`, `tailscale`
- **Region/Location**: `aws_region_us_east_1`, `hcloud_loc_fsn1`, `do_region_nyc1`
- **Instance type**: `aws_type_t3_micro`, `hcloud_type_cx21`
- **Environment**: `env_production`, `env_staging` (from tags/labels)
- **Role**: `role_webserver`, `role_database` (from tags/labels)
- **OS**: `os_ubuntu`, `os_debian`, `os_centos`
- **Status**: `online`, `offline`, `running`, `stopped`

## Tagging Best Practices

For automatic group creation, use consistent tagging:

### AWS EC2
```
Environment: production
Role: webserver
Project: myapp
```

### Hetzner Cloud (Labels)
```
env=production
role=webserver
project=myapp
```

### DigitalOcean (Tags)
```
env:production
role:webserver
project:myapp
```

### Tailscale/Headscale (Tags)
```
tag:ansible-production
tag:ansible-webserver
```

## Troubleshooting

### Debug inventory
```bash
ansible-inventory -i inventories/dynamic/aws.aws_ec2.yml --list --yaml
ansible-inventory -i inventories/dynamic/aws.aws_ec2.yml --graph
```

### Test connectivity
```bash
ansible -i inventories/dynamic/aws.aws_ec2.yml all -m ping
ansible -i inventories/dynamic/hcloud.yml all -m ping -u root
```

### Check specific host
```bash
ansible-inventory -i inventories/dynamic/aws.aws_ec2.yml --host web-server-1
```

### Common issues

1. **No hosts returned**: Check API credentials and filters
2. **Connection refused**: Verify security groups/firewalls allow SSH
3. **Permission denied**: Check `ansible_user` is correct for the OS
4. **Cache stale**: Clear cache with `rm -rf /tmp/ansible_*_cache`
5. **Plugin not found**: Install the required collection with `ansible-galaxy collection install <name>`
