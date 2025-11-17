# PHASE 3 Enterprise Infrastructure Framework - Deployment Guide

**Version:** 3.0 (Complete Framework)
**Release Date:** November 17, 2025
**Status:** Production-Ready
**Maintenance:** Sentinel Infrastructure Team

---

## Quick Start (15 minutes)

### Prerequisites
```bash
# Verify requirements
ansible --version          # 2.10 or higher
python3 --version         # 3.8 or higher
ssh -V                    # OpenSSH available

# Clone repository
git clone <repo-url> ansible-infra
cd ansible-infra
```

### 5-Step Deployment

```bash
# 1. Configure inventory
cp inventory.example.yml inventory.yml
vim inventory.yml  # Edit with your infrastructure details

# 2. Set up variables
mkdir -p group_vars host_vars
cp group_vars.example.yml group_vars/all.yml
vim group_vars/all.yml  # Configure for your environment

# 3. Verify connectivity
ansible all -i inventory.yml -m ping

# 4. Run deployment
ansible-playbook -i inventory.yml playbooks/site.yml

# 5. Verify installation
kubectl get nodes
kubectl get pods -A
```

---

## Detailed Deployment

### Phase 1: Pre-Deployment Planning (30 minutes)

#### 1.1 Infrastructure Assessment

**Questions to answer:**
- How many nodes do you need?
- What is your expected workload?
- How much storage do you need?
- What is your disaster recovery strategy?

**Example sizing:**
```
Small (dev/test):
- 1 control plane node (2 CPU, 4GB RAM)
- 2 worker nodes (2 CPU, 4GB RAM each)

Medium (production):
- 3 control plane nodes (4 CPU, 8GB RAM each)
- 5 worker nodes (4 CPU, 8GB RAM each)

Large (enterprise):
- 5 control plane nodes (8 CPU, 16GB RAM each)
- 20+ worker nodes (8 CPU, 16GB RAM each)
```

#### 1.2 Network Planning

**Define:**
- Pod network CIDR (default: 10.244.0.0/16)
- Service CIDR (default: 10.96.0.0/12)
- Node network topology
- DNS servers
- NTP servers

```yaml
# Example network configuration
kubernetes_pod_network_cidr: "10.244.0.0/16"
kubernetes_service_cidr: "10.96.0.0/12"
cluster_domain: "cluster.local"
dns_servers:
  - 10.0.0.1   # Your DNS server
  - 8.8.8.8    # Public fallback
```

#### 1.3 Security Planning

**Define:**
- RBAC policies
- Network policies
- Secret management strategy
- Certificate requirements
- Backup encryption

```yaml
# Example security configuration
service_mesh_mtls_mode: "STRICT"
disaster_recovery_encryption_enabled: true
disaster_recovery_encryption_algorithm: "AES-256-CBC"
rbac_enabled: true
network_policies_enabled: true
```

### Phase 2: Infrastructure Preparation (45 minutes)

#### 2.1 Provision Nodes

**Option A: Manual Provisioning**

```bash
# On each node
sudo apt-get update
sudo apt-get install -y openssh-server openssh-client python3 python3-pip
sudo systemctl enable ssh
sudo systemctl start ssh
```

**Option B: Cloud Automation**

```bash
# Using Terraform or other IaC tools
terraform apply -var="node_count=5" -var="node_type=t3.xlarge"
```

#### 2.2 Prepare Ansible Control Node

```bash
# Install requirements
pip3 install ansible>=2.10 ansible-core>=2.13 jinja2 netaddr pyyaml

# Generate SSH keys if needed
ssh-keygen -t ed25519 -f ~/.ssh/id_ansible -N ""

# Distribute SSH keys to all nodes
for node in <node-ips>; do
  ssh-copy-id -i ~/.ssh/id_ansible.pub ubuntu@$node
done

# Test connectivity
ansible all -i inventory.yml -m ping
```

#### 2.3 Create Inventory File

```yaml
# inventory.yml
---
all:
  vars:
    ansible_user: ubuntu
    ansible_private_key_file: ~/.ssh/id_ansible
    ansible_become: yes
    ansible_become_method: sudo

  children:
    control_plane:
      hosts:
        cp-1:
          ansible_host: 10.0.1.10
        cp-2:
          ansible_host: 10.0.1.11
        cp-3:
          ansible_host: 10.0.1.12

    workers:
      hosts:
        worker-1:
          ansible_host: 10.0.2.10
        worker-2:
          ansible_host: 10.0.2.11
        worker-3:
          ansible_host: 10.0.2.12

    kubernetes:
      children:
        control_plane:
        workers:
```

### Phase 3: Framework Deployment (60-90 minutes)

#### 3.1 Deploy Foundation (PHASE 1)

```bash
# System hardening, monitoring, and security foundation
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t phase1 \
  -e "security_enabled=true" \
  -e "monitoring_enabled=true" \
  -v

# Expected: 20-30 minutes
# Check: SSH hardening, firewall rules, monitoring agents installed
```

#### 3.2 Deploy Advanced Services (PHASE 2)

```bash
# Advanced services: Docker, databases, service discovery
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t phase2 \
  -e "container_runtime=containerd" \
  -e "database_ha_enabled=true" \
  -v

# Expected: 30-40 minutes
# Check: Docker/Containerd running, databases initialized
```

#### 3.3 Deploy Orchestration (PHASE 3)

```bash
# Full Kubernetes orchestration with service mesh and observability
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t phase3 \
  -e "kubernetes_enabled=true" \
  -e "service_mesh_enabled=true" \
  -e "monitoring_enabled=true" \
  -v

# Expected: 30-50 minutes
# Check: Kubectl works, all nodes Ready, pods running
```

#### 3.4 Verify Complete Deployment

```bash
# Get cluster status
kubectl get nodes
# Expected: All nodes in "Ready" status

# Get all pods
kubectl get pods -A
# Expected: All pods in "Running" or "Completed" status

# Check cluster info
kubectl cluster-info
kubectl version --short

# Run test pod
kubectl run test-nginx --image=nginx:latest
kubectl wait --for=condition=ready pod/test-nginx --timeout=300s
kubectl delete pod test-nginx
```

### Phase 4: Post-Deployment Configuration (30 minutes)

#### 4.1 Configure Applications

```bash
# Create production namespace
kubectl create namespace production
kubectl label namespace production monitoring=enabled istio-injection=enabled

# Deploy sample application
ansible-playbook -i inventory.yml playbooks/deploy-app.yml \
  -e "app_name=demo-app" \
  -e "app_image=nginx:latest" \
  -e "deployment_namespace=production"

# Verify application
kubectl get deployment -n production
kubectl get svc -n production
kubectl port-forward -n production svc/demo-app 8080:80
# Visit: http://localhost:8080
```

#### 4.2 Configure Observability

```bash
# Access monitoring dashboards
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Visit: http://localhost:3000 (admin/admin)

kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit: http://localhost:9090

kubectl port-forward -n istio-system svc/kiali 20001:20001
# Visit: http://localhost:20001

# Verify metrics are flowing
curl -s http://localhost:9090/api/v1/query?query=up | jq '.data.result | length'
# Expected: Multiple targets reporting "up"
```

#### 4.3 Configure Backups

```bash
# Verify backup automation is running
ls -la /var/backups/kubernetes/

# Test backup procedure
sudo /var/backups/kubernetes/backup-etcd.sh

# Verify backup was created
ls -lh /var/backups/kubernetes/etcd/ | head -5

# Check backup cron job
crontab -l | grep backup
```

### Phase 5: Production Hardening (45 minutes)

#### 5.1 Security Hardening

```bash
# Apply network policies
kubectl apply -f roles/common/templates/network_policy.yaml.j2

# Verify RBAC is enforced
kubectl auth can-i get pods --as=system:serviceaccount:production:default
# Expected: "no"

# Verify mTLS is enabled
kubectl get peerauthentication -A
# Expected: STRICT mode

# Check pod security standards
kubectl label namespace production pod-security.kubernetes.io/enforce=restricted
```

#### 5.2 Backup Testing

```bash
# Perform test recovery (use test namespace)
kubectl create namespace test-recovery

# Restore from backup
kubectl apply -f /var/backups/kubernetes/applications/production-backup.yaml \
  --namespace=test-recovery

# Verify restoration
kubectl get all -n test-recovery

# Cleanup
kubectl delete namespace test-recovery
```

#### 5.3 Disaster Recovery Drill

```bash
# Document RTO/RPO targets
# RTO: 4 hours (Recovery Time Objective)
# RPO: 1 hour (Recovery Point Objective)

# Test failover scenarios:
# 1. Single node failure: kubectl drain node-name
# 2. Backup restoration: Test with backup files
# 3. Service mesh recovery: Restart control plane pods

# Document results and update runbooks
```

#### 5.4 Performance Baseline

```bash
# Establish baseline metrics
kubectl top nodes
kubectl top pods -A

# Document baseline:
# - Node CPU/Memory utilization
# - Pod CPU/Memory usage
# - Network throughput
# - Storage usage

# Create performance dashboard in Grafana
```

---

## Deployment Verification Checklist

### Infrastructure Layer ✅
- [ ] All nodes in "Ready" status
- [ ] Network connectivity verified between nodes
- [ ] DNS resolution working correctly
- [ ] NTP synchronization verified
- [ ] Firewall rules configured correctly

### Kubernetes Layer ✅
- [ ] `kubectl get nodes` shows all nodes ready
- [ ] `kubectl get pods -A` shows all pods running
- [ ] `kubectl cluster-info` shows all components
- [ ] System pods (DNS, proxy, etc.) running
- [ ] Metrics server collecting metrics
- [ ] Helm package manager working

### Container Runtime ✅
- [ ] Container runtime (Docker/Containerd) running
- [ ] `docker ps` or `ctr ps` shows containers
- [ ] Container images can be pulled
- [ ] Volume mounts working

### Networking ✅
- [ ] Pod-to-pod communication working
- [ ] Pod-to-service communication working
- [ ] External service access working
- [ ] Network policies enforced
- [ ] DNS resolution in pods working

### Service Mesh ✅
- [ ] Istio/Linkerd control plane running
- [ ] Sidecars injected into pods
- [ ] mTLS certificates generated
- [ ] VirtualServices routing traffic correctly
- [ ] Kiali dashboard accessible

### Monitoring & Observability ✅
- [ ] Prometheus collecting metrics
- [ ] Grafana dashboards accessible
- [ ] Elasticsearch receiving logs
- [ ] Kibana displaying logs
- [ ] Jaeger collecting traces
- [ ] Alerts configured and working

### Storage ✅
- [ ] Storage classes available
- [ ] PersistentVolumes provisioned
- [ ] PersistentVolumeClaims bound
- [ ] Data persistence working

### Disaster Recovery ✅
- [ ] Backup scripts in place
- [ ] Backup cron jobs configured
- [ ] Backups being created
- [ ] Backup encryption working
- [ ] Recovery procedures tested

---

## Troubleshooting Common Issues

### Issue: Nodes not joining cluster

```bash
# Check kubelet logs
ssh worker-node
sudo journalctl -u kubelet -n 50 -f

# Common causes:
# - Network connectivity issues
# - Firewall blocking ports
# - Certificate issues
# - CNI not installed

# Solution:
# 1. Check network connectivity
# 2. Verify firewall rules allow K8s ports
# 3. Restart kubelet
# 4. Reinstall CNI plugin if needed
```

### Issue: Pods pending/not starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Check available resources
kubectl describe nodes | grep -A 5 "Allocated"

# Common causes:
# - Insufficient resources
# - Image pull errors
# - Volume mount issues
# - Scheduling conflicts

# Solution:
# 1. Check node resources
# 2. Verify image is available
# 3. Check volume configuration
# 4. Check pod tolerations
```

### Issue: Service mesh not working

```bash
# Check Istio installation
kubectl get ns | grep istio
kubectl get pods -n istio-system

# Check sidecar injection
kubectl get pod <pod-name> -n <namespace> -o yaml | grep sidecar

# Check mTLS status
kubectl get peerauthentication -A

# Verify VirtualServices
kubectl get virtualservices -A

# Test connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never
```

### Issue: No metrics in Prometheus

```bash
# Check Prometheus targets
curl http://prometheus:9090/api/v1/targets

# Check ServiceMonitors
kubectl get servicemonitor -A

# Check metrics are being scraped
curl http://localhost:9090/api/v1/query?query=up

# Verify scrape interval
kubectl get servicemonitor -A -o yaml | grep interval
```

---

## Performance Optimization Tips

1. **Right-size resource requests and limits**
   - Monitor actual usage
   - Set requests = 90th percentile
   - Set limits = 1.5-2x requests

2. **Enable pod horizontal autoscaling**
   ```yaml
   minReplicas: 3
   maxReplicas: 10
   targetCPUUtilizationPercentage: 80
   ```

3. **Use node selectors and affinity**
   - Pin workloads to appropriate nodes
   - Spread replicas across nodes
   - Use pod anti-affinity for HA

4. **Optimize storage**
   - Use appropriate storage classes
   - Set retention policies
   - Monitor storage usage

5. **Monitor and log efficiently**
   - Use sampling for high-volume logs
   - Prune old data regularly
   - Use efficient metrics collection

---

## Security Best Practices

1. **RBAC (Role-Based Access Control)**
   - Principle of least privilege
   - Regular access reviews
   - Audit all changes

2. **Network Policies**
   - Default deny all traffic
   - Explicitly allow required traffic
   - Segment by namespace

3. **Pod Security Standards**
   - Use restricted profiles
   - Run as non-root
   - Use read-only filesystems

4. **Secrets Management**
   - Use Kubernetes Secrets with encryption
   - Consider external secret management
   - Regular rotation of credentials

5. **Backup & Disaster Recovery**
   - Regular backup testing
   - Offsite backup copies
   - Document recovery procedures

---

## Next Steps After Deployment

1. **Week 1: Stabilization**
   - Monitor cluster health
   - Review and tune alerts
   - Train operations team

2. **Week 2-4: Optimization**
   - Baseline performance metrics
   - Optimize resource allocations
   - Performance tuning

3. **Month 2: Production Hardening**
   - Security audit
   - Disaster recovery drill
   - Load testing

4. **Ongoing: Operations**
   - Regular backups
   - Security updates
   - Capacity planning

---

## Support Resources

- **Documentation**: See README.md and architecture documentation
- **Operational Runbooks**: See OPERATIONAL_RUNBOOKS.md
- **API Documentation**: `kubectl api-resources`
- **Official Documentation**: https://kubernetes.io/docs/

---

## Rollback Procedure

If something goes wrong:

```bash
# 1. Stop any ongoing operations
ansible all -i inventory.yml -m shell -a "sudo systemctl stop kubelet"

# 2. Restore from backup
sudo /var/backups/kubernetes/restore-etcd.sh

# 3. Restart services
ansible all -i inventory.yml -m shell -a "sudo systemctl start kubelet"

# 4. Verify cluster
kubectl get nodes
kubectl get pods -A
```

---

**Framework Status:** Production-Ready
**Last Updated:** November 17, 2025
**Next Update:** December 17, 2025
