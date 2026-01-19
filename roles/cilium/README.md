# Cilium Role

Installs and configures Cilium CNI with kube-proxy replacement for K3s and RKE2 clusters.

## Features

- ✅ Automatic Cilium CLI installation with version pinning
- ✅ Checksum verification for security
- ✅ Support for K3s and RKE2
- ✅ Architecture-aware (amd64/arm64)
- ✅ Idempotent execution
- ✅ Comprehensive error handling with automatic rollback
- ✅ Optional connectivity testing
- ✅ Version verification after installation

## Requirements

- K3s or RKE2 cluster
- kubectl access configured
- **K3s:** Must be started with `--disable-kube-proxy --flannel-backend=none`
- **RKE2:** Must have `/etc/rancher/rke2/config.yaml` with appropriate CNI config

## Role Variables

Available variables with their default values (see `defaults/main.yml`):

```yaml
# Enable or disable Cilium installation
cilium_enabled: false

# Cilium CLI version (pinned for reproducibility)
# Latest as of 2025-10-01
cilium_cli_version: "v0.18.7"

# Cilium container version (deployed to cluster)
# Latest as of 2025-10-01
cilium_version: "1.18.2"

# Cilium kube-proxy replacement mode (true = full replacement, false = disabled)
cilium_kube_proxy_replacement: true

# Additional Cilium install options (list)
cilium_install_opts: []

# Cilium CLI binary path
cilium_cli_path: /usr/local/bin/cilium

# Temporary download directory
cilium_tmp_dir: /tmp

# Installation timeout (seconds)
cilium_install_timeout: 600

# Wait for Cilium to be ready after installation
cilium_wait_for_ready: true
cilium_ready_timeout: 300

# Fail the role if Cilium is not ready (recommended for production)
cilium_fail_on_not_ready: false

# Verify checksums for downloaded binaries (recommended)
# Note: If checksum file is not available, role will warn and proceed
cilium_verify_checksum: true

# Run connectivity test after installation (slow but thorough)
cilium_connectivity_test: false

# LoadBalancer IP pool configuration
# Enable to create a Cilium LoadBalancer IP pool (e.g., for WireGuard mesh IPs)
cilium_lb_pool_enabled: false

# LoadBalancer IP pool name
cilium_lb_pool_name: "mesh-pool"

# LoadBalancer IP pool source
# Options:
#   - "wireguard": Automatically detect WireGuard IP from wg0 interface
#   - "custom": Use cilium_lb_pool_ip variable
cilium_lb_pool_source: "wireguard"

# Custom LoadBalancer IP (used when cilium_lb_pool_source: "custom")
cilium_lb_pool_ip: ""

# WireGuard interface name (used when cilium_lb_pool_source: "wireguard")
cilium_lb_pool_wg_interface: "wg0"
```

## Dependencies

None

## Example Playbook

### K3s Basic Usage (Local Environment)

```yaml
- hosts: local-crunch
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
```

### K3s Production Usage with Strict Validation

```yaml
- hosts: all-crunch
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        cilium_kube_proxy_replacement: true
        cilium_fail_on_not_ready: true  # Fail if Cilium not ready
        cilium_connectivity_test: true   # Run connectivity test
        cilium_install_opts:
          - "--set ipam.mode=kubernetes"
          - "--set tunnel=vxlan"
```

### RKE2 Usage (Sensors)

**Important:** RKE2 requires additional configuration before running this role.

1. Create `/etc/rancher/rke2/config.yaml`:
```yaml
disable-kube-proxy: true
cni:
  - none  # Disable default Canal CNI
```

2. Run the playbook:
```yaml
- hosts: sensors
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        kubeconfig_path: /etc/rancher/rke2/rke2.yaml  # RKE2 kubeconfig path
        cilium_kube_proxy_replacement: true
```

### Custom Cilium Version

```yaml
- hosts: all-crunch
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        cilium_cli_version: "v0.18.7"  # CLI version
        cilium_version: "1.18.2"       # Container version
```

### With LoadBalancer IP Pool (WireGuard Mesh)

```yaml
- hosts: all-crunch
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        cilium_kube_proxy_replacement: true
        cilium_lb_pool_enabled: true          # Enable LoadBalancer IP pool
        cilium_lb_pool_source: "wireguard"    # Auto-detect from WireGuard
        cilium_install_opts:
          - "--set k8sServiceHost=127.0.0.1"
          - "--set k8sServicePort=6443"
```

This will:
1. Install Cilium with kube-proxy replacement
2. Detect the WireGuard IP from `wg0` interface
3. Create a Cilium LoadBalancer IP pool with that IP
4. Allow LoadBalancer services to use the WireGuard mesh IP

### With Custom LoadBalancer IP

```yaml
- hosts: special-host
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        cilium_lb_pool_enabled: true
        cilium_lb_pool_source: "custom"       # Use custom IP
        cilium_lb_pool_ip: "10.50.0.100"      # Custom IP address
        cilium_lb_pool_name: "custom-pool"    # Custom pool name
```

## Testing

### Local Environment Testing

```bash
# Deploy to local
ansible-playbook playbooks/deploy-local.yml

# Verify Cilium status
ansible local-crunch -m shell -a "cilium status --wait" -b

# Check kube-proxy is disabled (should return nothing)
ansible local-crunch -m shell -a "kubectl get pods -n kube-system | grep kube-proxy" -b

# Verify Cilium pods are running
ansible local-crunch -m shell -a "kubectl get pods -n kube-system -l k8s-app=cilium" -b

# Check Cilium version
ansible local-crunch -m shell -a "cilium version" -b
```

### Production Testing

```bash
# Deploy to canary host first
ansible-playbook playbooks/crunch.yml -l canary01-crunch

# Monitor for 1 week before rolling out to all hosts
```

## Troubleshooting

### Cilium pods not starting

```bash
# Check Cilium status
cilium status --wait

# Check pod logs
kubectl logs -n kube-system -l k8s-app=cilium --tail=100

# Check for common issues
kubectl get pods -n kube-system | grep -E "cilium|kube-proxy"

# Common issue: kube-proxy still running
kubectl get pods -n kube-system | grep kube-proxy
# If found, kube-proxy was not properly disabled
# Fix: Restart K3s/RKE2 with correct flags
```

### Network connectivity issues

```bash
# Run connectivity test
cilium connectivity test --test-concurrency=1

# Check for conflicting CNI
ls /etc/cni/net.d/
# Should only see cilium config (10-cilium.conflist)

# Check Cilium agent status
kubectl get pods -n kube-system -l k8s-app=cilium -o wide
kubectl describe pods -n kube-system -l k8s-app=cilium

# Check Cilium operator
kubectl get deployment -n kube-system cilium-operator
kubectl logs -n kube-system deployment/cilium-operator
```

### Installation fails with checksum error

```bash
# If checksum file is not available for your version, the role will warn and proceed
# To disable checksum verification entirely (not recommended for production):
cilium_verify_checksum: false

# Or manually verify checksums after download:
cd /tmp
wget https://github.com/cilium/cilium-cli/releases/download/v0.18.7/cilium-linux-amd64.tar.gz.sha256sum
sha256sum -c cilium-linux-amd64.tar.gz.sha256sum
```

**Note:** The role now gracefully handles missing checksum files. If the checksum file is not available (404 error), it will log a warning and proceed with installation. For maximum security in production, manually verify the binary or use a version that includes checksum files.

### Kubeconfig not found

```bash
# Check kubeconfig path
ls -la /etc/rancher/k3s/k3s.yaml   # K3s
ls -la /etc/rancher/rke2/rke2.yaml # RKE2

# Verify K3s/RKE2 is running
systemctl status k3s           # K3s
systemctl status rke2-server   # RKE2

# Test kubectl access
kubectl --kubeconfig=/etc/rancher/k3s/k3s.yaml get nodes
```

### Cilium not ready after timeout

```bash
# Check events
kubectl get events -n kube-system --sort-by='.lastTimestamp'

# Check node status
kubectl get nodes -o wide

# Check system resources
free -h
df -h /var

# Increase ready timeout
cilium_ready_timeout: 600  # 10 minutes
```

### Services not accessible after Cilium installation

```bash
# Check Cilium network policies
kubectl get networkpolicies -A

# Check service endpoints
kubectl get endpoints -A

# Check Cilium connectivity
cilium connectivity test

# Verify kube-proxy is disabled
kubectl get daemonset -n kube-system kube-proxy
# Should return: Error from server (NotFound)
```

## Rollback Procedures

### Automatic Rollback

The role includes automatic rollback on failure via the `Rollback Cilium on failure` handler.

### Manual Rollback for K3s

```bash
# SSH to the affected node
ssh user@crunch-node

# Uninstall Cilium
cilium uninstall --wait

# Edit K3s service to remove Cilium flags
sudo systemctl edit --full k3s.service
# Remove: --disable-kube-proxy --flannel-backend=none

# Reload systemd and restart K3s
sudo systemctl daemon-reload
sudo systemctl restart k3s

# Wait for Flannel to return (2-3 minutes)
kubectl get pods -n kube-system | grep flannel
# Should see: kube-flannel-xxx

# Verify services are working
kubectl get svc -A
kubectl get endpoints -A
```

### Manual Rollback for RKE2

```bash
# SSH to the affected node
ssh user@sensor-node

# Uninstall Cilium
cilium uninstall --wait

# Remove Cilium config from RKE2
sudo rm /etc/rancher/rke2/config.yaml
# Or edit and remove CNI settings

# Restart RKE2 to restore Canal
sudo systemctl restart rke2-server

# Wait for Canal to redeploy (2-3 minutes)
kubectl get pods -n kube-system | grep -E "canal|calico|flannel"
# Should see Canal components

# Verify node is ready
kubectl get nodes

# Verify services are working
kubectl get svc -A
```

### Rollback via Ansible

```yaml
# Create rollback playbook
- hosts: target-host
  tasks:
    - name: Uninstall Cilium
      ansible.builtin.command: cilium uninstall --wait
      environment:
        KUBECONFIG: /etc/rancher/k3s/k3s.yaml

    - name: Remove Cilium flags from K3s (manual step required)
      ansible.builtin.debug:
        msg: "Manually edit /etc/systemd/system/k3s.service to remove Cilium flags"

    - name: Restart K3s
      ansible.builtin.systemd:
        name: k3s
        state: restarted
        daemon_reload: yes
```

### Verification After Rollback

```bash
# Check default CNI is back
kubectl get pods -n kube-system | grep -E "flannel|canal|calico"

# Verify services work
kubectl get svc -A
kubectl get endpoints -A

# Test pod-to-pod connectivity
kubectl run test-pod --image=busybox --rm -it -- ping <another-pod-ip>

# Check kube-proxy is running (if not using Cilium)
kubectl get pods -n kube-system | grep kube-proxy
```

## Upgrading Cilium

To upgrade to a new Cilium version:

```yaml
- hosts: target-hosts
  roles:
    - role: cilium
      vars:
        cilium_enabled: true
        cilium_version: "1.15.0"  # New version
        cilium_cli_version: "v0.16.0"  # New CLI version
```

**Note:** Cilium upgrades are handled automatically by the role. The CLI will perform a rolling upgrade.

## Security Considerations

- ✅ Checksum verification enabled by default (`cilium_verify_checksum: true`)
- ✅ Downloads from official GitHub releases only
- ✅ Version pinning prevents unexpected upgrades
- ⚠️  Role runs as root (required for CNI installation)
- ⚠️  Ensure kubeconfig permissions are restricted (0600)

## Performance Tuning

```yaml
# For resource-constrained environments
cilium_install_opts:
  - "--set operator.replicas=1"
  - "--set hubble.enabled=false"
  - "--set prometheus.enabled=false"

# For production with monitoring
cilium_install_opts:
  - "--set prometheus.enabled=true"
  - "--set operator.prometheus.enabled=true"
  - "--set hubble.enabled=true"
  - "--set hubble.metrics.enabled=true"
```

## License

Proprietary - Corelight

## Author Information

Corelight Infrastructure Team

## Changelog

### Version 2.1 (2025-10-01)
- Updated to Cilium CLI v0.18.7 (latest)
- Updated to Cilium v1.18.2 (latest)
- Fixed checksum URL format
- Made checksum verification graceful (warns if checksum unavailable)
- Fixed version string format in download URLs

### Version 2.0 (2025-10-01)
- Added version pinning for Cilium CLI and container
- Added checksum verification
- Added kubeconfig validation
- Added binary validation
- Improved error handling with rescue block
- Added automatic rollback on failure
- Added connectivity test option
- Fixed shell command security issue
- Comprehensive documentation updates

### Version 1.0 (2024)
- Initial release
- Basic Cilium installation
- K3s and RKE2 support
