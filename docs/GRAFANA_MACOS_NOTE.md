# Grafana Collection - macOS Support Note

## Situation

The official `grafana.grafana` collection may not fully support macOS deployment out of the box. Some components like systemd-dependent services need platform-specific implementations.

## Current Approach

We have two options:

### Option 1: Fork & Customize (Recommended for macOS)
If full macOS support is required:

```bash
# Fork the Grafana collection
git clone https://github.com/grafana/grafana-ansible-collection grafana-collection-custom
cd grafana-collection-custom

# Make macOS-specific modifications
# - Handle launchd instead of systemd
# - Use brew for package installation
# - Adapt configuration paths

# Reference in requirements.yml
collections:
  - name: grafana.grafana_custom
    src: file:///path/to/grafana-collection-custom
```

### Option 2: Conditional Integration
Use the official collection for Linux, implement macOS-specific tasks:

```yaml
- name: Deploy Grafana Agent
  block:
    # Use official Grafana collection role for Linux
    - role: grafana.grafana.grafana_agent
      when: ansible_os_family != "Darwin"

  block:
    # Custom macOS implementation
    - name: Install Grafana Agent on macOS
      homebrew:
        name: grafana-agent
        state: present
      when: ansible_os_family == "Darwin"
```

## Recommendation

**Use Option 2 (Conditional Integration)** initially:
- Leverage official collection for Linux (well-tested, maintained)
- Implement custom macOS tasks in the common role
- Keep maintenance burden manageable
- Can fork if needed later

## Implementation Plan

### Phase 2 Action Items

1. Test Grafana collection on Linux servers
2. Implement macOS-specific Grafana Agent tasks
3. Create platform-specific handlers
4. Document macOS limitations and workarounds
5. Consider forking if extensive customization needed

## macOS Considerations

- Grafana Agent: Available via brew, works well
- Prometheus: Can run locally, needs launchd service wrapper
- Loki: Lightweight, suitable for macOS
- Node Exporter: Homebrew package available
- Systemd: Not available - use launchd instead

## Resources

- [Grafana Agent Brew Formula](https://formulae.brew.sh/formula/grafana-agent)
- [Grafana Ansible Collection](https://galaxy.ansible.com/grafana/grafana)
- [Creating launchd Services](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)

## Next Steps

1. Evaluate official collection on Linux servers first
2. If issues arise with macOS, implement Option 2
3. Document any workarounds in this file
4. Plan for forking if extensive customization needed
