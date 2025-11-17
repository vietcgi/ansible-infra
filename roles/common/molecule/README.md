# Molecule Tests - Common Role

Testing framework for the `common` role using Molecule and Docker.

## Overview

Molecule enables development and testing of Ansible roles in isolation. This test suite validates the `common` role across multiple Linux distributions.

## Test Scenarios

### Default Scenario

Tests the common role on multiple platforms:

- **Ubuntu 24.04 LTS** - Latest stable release
- **Ubuntu 22.04 LTS** - Long-term support version
- **Debian 12** - Current stable Debian
- **Rocky 9** - RHEL-compatible distribution

## Quick Start

### Prerequisites

```bash
# Install Molecule and dependencies
pip install molecule molecule-docker ansible-lint

# Or use the project's make command
make install-dev
```

### Run Tests

```bash
# Run complete test lifecycle (default scenario)
molecule test

# Specific test phases:
molecule dependency # Install role dependencies
molecule lint # Run ansible-lint
molecule create # Create test instances
molecule prepare # Prepare instances
molecule converge # Apply role to instances
molecule idempotence # Verify idempotence
molecule verify # Run verification tests
molecule destroy # Clean up instances

# Debug running instance
molecule create
molecule converge
molecule login ubuntu-24 # SSH into instance
# ... test manually ...
molecule destroy
```

## Test Phases

### 1. Dependency
Installs any role dependencies (currently none).

### 2. Lint
Runs ansible-lint in production profile to check code quality.

### 3. Create
Spins up Docker containers for each platform.

### 4. Prepare
Installs basic packages and configures test instances:
- Python 3
- curl
- Basic utilities
- systemd setup

### 5. Converge
Applies the `common` role to test instances.

Validates:
- All tasks execute successfully
- No errors or failures
- Configuration is applied

### 6. Idempotence
Runs the role a second time to verify idempotence.

Validates:
- Second run shows no changes
- Role is safe to run repeatedly
- No configuration drift

### 7. Verify
Runs comprehensive verification tests:

**OS Validation**
- ✓ OS family detected
- ✓ Distribution recognized

**Packages**
- ✓ System updated
- ✓ Core packages installed (curl, git, vim, etc.)

**Python**
- ✓ Python 3 available
- ✓ pip configured

**NTP**
- ✓ Time synchronization enabled
- ✓ Services running

**SSH**
- ✓ SSH config valid
- ✓ Permissions correct (0600)
- ✓ Post-quantum algorithms enabled
- ✓ sshd syntax validated

**Kernel**
- ✓ sysctl parameters applied
- ✓ Network tuning in place

**Audit**
- ✓ Audit daemon running
- ✓ Logging operational

**File Limits**
- ✓ Descriptor limits configured
- ✓ Resource constraints applied

**DNS**
- ✓ Resolver configured
- ✓ Name resolution available

### 8. Destroy
Removes test containers and cleans up.

## What's Tested

### OS Detection
- Ubuntu 24.04, 22.04 (Debian family)
- Debian 12 (Debian family)
- Rocky 9 (RedHat family)

Tests verify:
- Distribution correctly identified
- Appropriate package managers used
- OS-specific tasks execute properly

### System Configuration

**Updates**
- Package cache updated
- Packages upgraded
- Security patches applied

**Package Management**
- Core utilities installed
- Python runtime configured
- Development headers available

**Time Synchronization**
- NTP service running
- Time synchronized
- Timezone configured

**SSH Hardening**
- Config file valid
- Permissions restrictive (0600)
- Post-quantum algorithms enabled
- Key-based auth enforced

**Kernel Optimization**
- sysctl parameters applied
- Network tuning active
- Performance optimization in place

**Security Controls**
- Audit logging enabled
- File limits configured
- Security parameters tuned

## Verifying Manually

To manually test and debug:

```bash
# Start instance but don't run tests
molecule create
molecule converge

# SSH into running instance
molecule login ubuntu-24

# Test things manually
ssh-keygen -t ed25519
cat /etc/ssh/sshd_config
timedatectl status
sysctl net.core.somaxconn

# When done
molecule destroy
```

## Common Issues

### Docker Not Running
```bash
# Start Docker daemon
docker ps

# If fails, start Docker Desktop or daemon
```

### Permission Denied
```bash
# Add your user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Out of Disk Space
```bash
# Clean up old containers and images
docker system prune -a
```

### SSH Fails in Container
```bash
# Make sure SSH is properly configured
molecule converge
ssh -vvv instance_name # Debug SSH

# Check sshd config
molecule login ubuntu-24
sudo sshd -T
```

## CI/CD Integration

Tests run in GitHub Actions on every PR. To replicate locally:

```bash
# Full test suite like CI
molecule test

# With verbose output
molecule test -vv

# Specific platform
molecule test -- --limit ubuntu-24
```

## Configuration Files

**molecule.yml**
- Defines test platforms (Ubuntu, Debian, Rocky)
- Configures Docker driver
- Sets up inventory
- Specifies playbooks

**converge.yml**
- Applies the role to instances
- Main test playbook

**prepare.yml**
- Sets up test instance prerequisites
- Installs basic packages
- Configures systemd

**verify.yml**
- Comprehensive verification tests
- Validates all role functionality
- Checks security controls
- Tests configuration

**requirements.yml**
- Specifies role dependencies (currently none)

## Troubleshooting

### Tests Hang
```bash
# Kill process and clean up
^C # Press Ctrl+C
molecule destroy
docker ps --all # Check for leftover containers
```

### SSH Issues
```bash
# Verify SSH is running
molecule converge
molecule login ubuntu-24
sudo systemctl status ssh

# Check sshd config
sudo sshd -T
```

### Package Installation Fails
```bash
# Check package manager availability
molecule login ubuntu-24
apt update # Debian
yum update # RedHat

# Try individual package
apt install -y curl
```

## Performance

Typical test times (on modern hardware):

| Phase | Time |
|-------|------|
| Create | 30-60 sec |
| Prepare | 20-30 sec |
| Converge | 60-120 sec |
| Idempotence | 30-60 sec |
| Verify | 30-60 sec |
| **Total** | **3-5 min** |

## Best Practices

1. **Always run tests before PR**
 ```bash
 molecule test
 ```

2. **Test idempotence**
 ```bash
 molecule idempotence
 ```

3. **Verify on all platforms**
 - Tests run on 4 distributions
 - Ensures cross-platform compatibility

4. **Check logs on failure**
 ```bash
 molecule converge -vv # Verbose output
 ```

5. **Clean up after testing**
 ```bash
 molecule destroy
 ```

## References

- [Molecule Documentation](https://molecule.readthedocs.io/)
- [Ansible Testing Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)
- [Docker Documentation](https://docs.docker.com/)

## Contributing

When adding features to the common role:

1. Write tests first (TDD approach)
2. Add verification tests in `verify.yml`
3. Run `molecule test` to validate
4. Ensure idempotence passes
5. Update this README if needed

---

**Last Updated**: November 15, 2025
**Status**: Production-Ready
