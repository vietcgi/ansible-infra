# Project: example-project

Infrastructure as Code for example-project using Ansible.

## Quick Start

1. **Define your servers**
 ```bash
 edit inventory.yml
 ```

2. **Configure defaults**
 ```bash
 edit group_vars/all.yml
 ```

3. **Set secrets**
 ```bash
 ansible-vault edit group_vars/all_vault.yml
 ```

4. **Test connectivity**
 ```bash
 ansible all -i . -m ping
 ```

5. **Deploy**
 ```bash
 ansible-playbook ../../../playbooks/provision.yml -i .
 ```

## Files

- **inventory.yml** - Server definitions
- **group_vars/all.yml** - Project-wide configuration
- **group_vars/<group>.yml** - Group-specific configuration
- **group_vars/all_vault.yml** - Encrypted secrets
- **host_vars/** - Host-specific configuration

## Documentation

- See [`../../README.md`](../../README.md) for framework overview
- See [`../../../docs/NEW_PROJECT_QUICKSTART.md`](../../../docs/NEW_PROJECT_QUICKSTART.md) for detailed guide
- See [`../../../docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) for technical details

## Variables

All available variables are documented in the role defaults:

- `../../common/defaults/main.yml`
- `../../system_hardening_macos/defaults/main.yml`

Override any variable in:
- `group_vars/all.yml` (project-wide)
- `group_vars/<group>.yml` (group-specific)
- `host_vars/<host>.yml` (host-specific)

## Support

- Questions? See the main [README](../../README.md)
- Issues? Check [TROUBLESHOOTING.md](../../../docs/TROUBLESHOOTING.md)
