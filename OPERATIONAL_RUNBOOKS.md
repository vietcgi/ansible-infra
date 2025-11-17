# PHASE 3 Operational Runbooks

**Framework Version:** 3.0 (PHASE 3 Complete)
**Last Updated:** November 17, 2025
**Status:** Production-Ready

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Initial Infrastructure Setup](#initial-infrastructure-setup)
3. [Kubernetes Cluster Deployment](#kubernetes-cluster-deployment)
4. [Application Deployment](#application-deployment)
5. [Service Mesh Integration](#service-mesh-integration)
6. [Monitoring & Observability Setup](#monitoring--observability-setup)
7. [Disaster Recovery Configuration](#disaster-recovery-configuration)
8. [Operational Procedures](#operational-procedures)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Emergency Procedures](#emergency-procedures)

---

## Pre-Deployment Checklist

### Infrastructure Requirements

**Hardware Requirements:**
- Control Plane Nodes: 2+ cores, 4GB+ RAM, 20GB+ disk
- Worker Nodes: 1+ core, 2GB+ RAM, 10GB+ disk per node
- Network: 100+ Mbps connectivity, low latency between nodes

**Software Requirements:**
- Ubuntu 22.04+ or RHEL 8+
- Python 3.8+ installed
- Ansible 2.10+ installed
- Docker or Containerd runtime (will be installed by framework)

### Pre-Flight Checks

```bash
# 1. Verify Ansible is installed
ansible --version

# 2. Verify SSH connectivity to all nodes
ansible all -i inventory -m ping

# 3. Verify Python on all nodes
ansible all -i inventory -m command -a "python3 --version"

# 4. Verify disk space (minimum 10GB)
ansible all -i inventory -m command -a "df -h / | tail -1"

# 5. Verify network connectivity between nodes
ansible all -i inventory -m command -a "ping -c 1 <controller_ip>"

# 6. Create backup of existing infrastructure
ansible all -i inventory -m command -a "tar -czf /tmp/system_backup.tar.gz /etc" \
  --check --diff
```

### Inventory Configuration

Create `inventory.yml`:

```yaml
---
all:
  vars:
    ansible_user: ubuntu
    ansible_password: "{{ vault_password }}"
    ansible_become: yes
    ansible_become_method: sudo
  children:
    control_plane:
      hosts:
        controller-1:
          ansible_host: 10.0.0.10
        controller-2:
          ansible_host: 10.0.0.11
    workers:
      hosts:
        worker-1:
          ansible_host: 10.0.0.20
        worker-2:
          ansible_host: 10.0.0.21
        worker-3:
          ansible_host: 10.0.0.22
    kubernetes:
      children:
        control_plane:
        workers:
```

---

## Initial Infrastructure Setup

### Step 1: Prepare Systems

```bash
# Run initial system preparation
ansible-playbook -i inventory.yml playbooks/init.yml \
  -e "configure_firewall=true" \
  -e "enable_ipv6=false"

# Expected tasks:
# - Update package manager
# - Install required packages
# - Configure networking
# - Set up system limits
# - Configure firewall rules
```

### Step 2: Configure Variables

Create `group_vars/all.yml`:

```yaml
---
# Cluster Configuration
kubernetes_enabled: true
kubernetes_version: "1.28.0"
kubernetes_cluster_name: "prod-cluster"
kubernetes_pod_network_cidr: "10.244.0.0/16"
kubernetes_service_cidr: "10.96.0.0/12"

# Container Runtime
container_runtime: "containerd"
containerd_version: "1.7.0"

# Networking
cni_plugin: "flannel"
flannel_version: "0.22.0"
dns_servers: ["8.8.8.8", "8.8.4.4"]

# Storage
persistent_volume_enabled: true
storage_class_name: "fast"
storage_path: "/var/lib/kubernetes/volumes"

# Service Mesh
service_mesh_enabled: true
service_mesh_type: "istio"  # or "linkerd"
service_mesh_istio_version: "1.18.0"
service_mesh_mtls_mode: "STRICT"

# Disaster Recovery
disaster_recovery_enabled: true
backup_storage_path: "/var/backups/kubernetes"
disaster_recovery_rto: "4h"
disaster_recovery_rpo: "1h"
disaster_recovery_encryption_enabled: true

# Monitoring
monitoring_enabled: true
monitoring_prometheus_enabled: true
monitoring_jaeger_enabled: true
monitoring_elasticsearch_enabled: true
prometheus_retention_days: 15
grafana_admin_password: "{{ vault_grafana_password }}"
```

---

## Kubernetes Cluster Deployment

### Step 1: Deploy Kubernetes Foundation

```bash
# Run Kubernetes orchestration wrapper
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t kubernetes_orchestration \
  --extra-vars "@group_vars/all.yml"

# Expected duration: 10-15 minutes
# Expected output:
# - containerd installed and configured
# - kubeadm initialized
# - Flannel CNI deployed
# - kubelet configured on all nodes
```

### Step 2: Verify Cluster Health

```bash
# Check cluster status
kubectl get nodes
# Expected: All nodes in "Ready" status

# Check system pods
kubectl get pods -n kube-system
# Expected: All system pods running

# Check cluster info
kubectl cluster-info

# Test cluster connectivity
kubectl run test-pod --image=nginx:latest
kubectl logs test-pod
kubectl delete pod test-pod
```

### Step 3: Configure Helm

```bash
# Helm is automatically installed by the wrapper
helm version

# Add Helm repositories
helm repo add stable https://charts.helm.sh/stable
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Step 4: Configure Metrics Server

```bash
# Metrics server is automatically installed
kubectl get deployment metrics-server -n kube-system

# Verify metrics are working (wait 60 seconds after deployment)
kubectl top nodes
kubectl top pods -A
```

---

## Application Deployment

### Step 1: Create Deployment Namespace

```bash
kubectl create namespace production

# Label namespace for monitoring
kubectl label namespace production monitoring=enabled
kubectl label namespace production istio-injection=enabled  # For service mesh
```

### Step 2: Deploy Application

```bash
# Using the application deployment wrapper
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t application_deployment \
  -e "app_name=myapp" \
  -e "app_image=docker.io/myorg/myapp:1.0.0" \
  -e "deployment_namespace=production" \
  -e "app_replicas=3" \
  -e "app_container_port=8080" \
  -e "app_cpu_request=100m" \
  -e "app_cpu_limit=500m" \
  -e "app_memory_request=128Mi" \
  -e "app_memory_limit=512Mi" \
  --extra-vars "@group_vars/all.yml"

# Expected duration: 2-3 minutes
```

### Step 3: Verify Application Deployment

```bash
# Check deployment status
kubectl get deployment -n production

# Check rollout status
kubectl rollout status deployment/myapp -n production

# Check pods are running
kubectl get pods -n production
# Expected: 3 pods in "Running" status

# Verify application is accessible
kubectl port-forward -n production svc/myapp-service 8080:8080
curl http://localhost:8080/health

# Check application logs
kubectl logs -n production deployment/myapp -f
```

### Step 4: Scale Application

```bash
# Manual scaling
kubectl scale deployment myapp --replicas=5 -n production

# Verify scaling
kubectl get pods -n production | wc -l

# Check HPA status
kubectl get hpa -n production
# Expected: Scales based on CPU/memory metrics
```

---

## Service Mesh Integration

### Step 1: Deploy Service Mesh

```bash
# Deploy Istio (or Linkerd)
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t service_mesh_integration \
  -e "service_mesh_enabled=true" \
  -e "service_mesh_type=istio" \
  --extra-vars "@group_vars/all.yml"

# Expected duration: 5-10 minutes
# Expected output:
# - Istio control plane deployed
# - Ingress gateway configured
# - mTLS policies applied
```

### Step 2: Verify Service Mesh Installation

```bash
# Check Istio namespaces
kubectl get namespace | grep istio

# Check Istio components
kubectl get pods -n istio-system

# Verify mTLS is enabled
kubectl get peerauthentication -A

# Check VirtualServices
kubectl get virtualservices -n production
```

### Step 3: Configure Traffic Management

```yaml
# Create VirtualService for canary deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: myapp-vs
  namespace: production
spec:
  hosts:
  - myapp
  http:
  - match:
    - headers:
        user-agent:
          regex: ".*Chrome.*"
    route:
    - destination:
        host: myapp-service
        subset: v2
      weight: 20
    - destination:
        host: myapp-service
        subset: v1
      weight: 80
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
```

### Step 4: Monitor Service Mesh

```bash
# Access Kiali dashboard
kubectl port-forward -n istio-system svc/kiali 20001:20001
# Visit: http://localhost:20001

# View distributed traces in Jaeger
kubectl port-forward -n istio-system svc/jaeger-collector 16686:16686
# Visit: http://localhost:16686
```

---

## Monitoring & Observability Setup

### Step 1: Deploy Monitoring Stack

```bash
# Deploy observability components
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t advanced_monitoring \
  --extra-vars "@group_vars/all.yml"

# Expected duration: 5-8 minutes
# Expected output:
# - Prometheus deployed
# - Grafana configured
# - Elasticsearch for logs
# - Jaeger for distributed tracing
```

### Step 2: Access Monitoring Dashboards

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Visit: http://localhost:9090
# Verify targets are "UP"

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Visit: http://localhost:3000
# Default credentials: admin/admin

# Kiali (Service Mesh)
kubectl port-forward -n istio-system svc/kiali 20001:20001
# Visit: http://localhost:20001

# Kibana (Logs)
kubectl port-forward -n observability svc/kibana 5601:5601
# Visit: http://localhost:5601

# Jaeger (Traces)
kubectl port-forward -n observability svc/jaeger-query 16686:16686
# Visit: http://localhost:16686
```

### Step 3: Verify Metrics Collection

```bash
# Check Prometheus scrape targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, state: .health}'

# Check Elasticsearch indexes
curl -s http://elasticsearch:9200/_cat/indices | head -20

# Verify Jaeger is receiving traces
# Check application logs for trace IDs
kubectl logs -n production deployment/myapp | grep "trace"
```

### Step 4: Configure Alerting

```yaml
# Example Prometheus AlertRule for application
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: myapp-alerts
  namespace: production
spec:
  groups:
  - name: myapp
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "High error rate detected"

    - alert: HighLatency
      expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
      for: 5m
      annotations:
        summary: "High latency detected"

    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
      for: 5m
      annotations:
        summary: "High memory usage"
```

---

## Disaster Recovery Configuration

### Step 1: Configure Backups

```bash
# Deploy disaster recovery automation
ansible-playbook -i inventory.yml playbooks/site.yml \
  -t disaster_recovery \
  -e "backup_storage_path=/var/backups/kubernetes" \
  -e "disaster_recovery_encryption_enabled=true" \
  --extra-vars "@group_vars/all.yml"

# Expected: Backup scripts installed at /var/backups/kubernetes/
```

### Step 2: Verify Backup Configuration

```bash
# Check backup scripts are in place
ls -la /var/backups/kubernetes/

# List available backup scripts
ls -la /var/backups/kubernetes/backup-*.sh

# Check backup schedule (cron jobs)
crontab -l | grep backup

# Expected: Backups scheduled at regular intervals (e.g., hourly, daily)
```

### Step 3: Test Backup Functionality

```bash
# Perform manual backup
sudo /var/backups/kubernetes/backup-etcd.sh
# Expected: New encrypted backup file created

# Verify backup integrity
ls -lh /var/backups/kubernetes/etcd/ | head -5

# Test backup encryption
file /var/backups/kubernetes/etcd/snapshot*.enc
# Expected: Data file (encrypted)

# List application backup
sudo /var/backups/kubernetes/backup-applications.sh
# Expected: All namespaces backed up
```

### Step 4: Test Recovery Procedures

```bash
# Simulate recovery from backup
# Do NOT run on production without careful planning

# 1. Create a test namespace
kubectl create namespace test-recovery

# 2. Restore application from backup
kubectl apply -f /var/backups/kubernetes/applications/production-backup.yaml \
  --namespace=test-recovery

# 3. Verify restoration
kubectl get deployments -n test-recovery

# 4. Clean up test namespace
kubectl delete namespace test-recovery
```

---

## Operational Procedures

### Daily Operations

```bash
# 1. Check cluster health
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running

# 2. Review monitoring dashboards
# - Grafana: Application metrics
# - Kiali: Service mesh visualization
# - Kibana: Application logs

# 3. Check backup status
ls -lh /var/backups/kubernetes/etcd/ | head -5

# 4. Review alerts
# Visit Prometheus: http://localhost:9090/alerts
# Check AlertManager: http://localhost:9093
```

### Weekly Operations

```bash
# 1. Review cluster capacity
kubectl top nodes
kubectl describe nodes | grep -E "Allocatable|Allocated"

# 2. Review persistent volumes
kubectl get pv,pvc -A

# 3. Check certificate expiration
sudo kubeadm certs check-expiration

# 4. Review application performance
# Check Grafana for trends
# Review Jaeger for trace patterns
```

### Monthly Operations

```bash
# 1. Full cluster backup test
sudo /var/backups/kubernetes/backup-etcd.sh
sudo /var/backups/kubernetes/backup-applications.sh

# 2. Review security logs
# Check audit logs in Elasticsearch

# 3. Update components
# Review available updates
ansible-galaxy install -r requirements.yml --upgrade

# 4. Capacity planning review
# Analyze growth trends
# Plan for scaling
```

---

## Troubleshooting Guide

### Cluster Issues

**Symptom: Nodes in "NotReady" status**

```bash
# 1. Check node status
kubectl describe node <node-name>

# 2. Check kubelet status
ssh <node-ip>
sudo systemctl status kubelet
sudo journalctl -u kubelet -n 50

# 3. Check system pods
kubectl get pods -n kube-system | grep -E "coredns|flannel"

# 4. Check disk space
df -h / /var/lib/kubelet

# 5. Restart kubelet if needed
sudo systemctl restart kubelet
```

**Symptom: Pods unable to schedule**

```bash
# 1. Check pod events
kubectl describe pod <pod-name> -n <namespace>

# 2. Check resource availability
kubectl describe nodes | grep -E "Allocated|Available"

# 3. Check taints and tolerations
kubectl describe node <node-name> | grep Taints

# 4. Increase node capacity or add new nodes
```

### Application Issues

**Symptom: Application pods in "Pending" status**

```bash
# 1. Check pod events
kubectl describe pod <pod-name> -n production

# 2. Check resource requests
kubectl get pod <pod-name> -n production -o yaml | grep -A 5 resources

# 3. Check node capacity
kubectl top nodes
kubectl describe nodes | grep Allocated

# 4. Solutions:
# - Scale down other applications
# - Add more worker nodes
# - Reduce resource requests
```

**Symptom: Application crashing (CrashLoopBackOff)**

```bash
# 1. Check pod logs
kubectl logs <pod-name> -n production
kubectl logs <pod-name> -n production --previous

# 2. Check resource usage
kubectl top pod <pod-name> -n production

# 3. Check liveness probe configuration
kubectl get pod <pod-name> -n production -o yaml | grep -A 10 livenessProbe

# 4. Check readiness probe configuration
kubectl get pod <pod-name> -n production -o yaml | grep -A 10 readinessProbe
```

### Networking Issues

**Symptom: Service unable to reach backend pods**

```bash
# 1. Check endpoints
kubectl get endpoints -n production

# 2. Check network policies
kubectl get networkpolicy -n production
kubectl describe networkpolicy <policy-name> -n production

# 3. Test connectivity
kubectl exec -it <pod-name> -n production -- sh
ping <service-ip>
curl http://<service-name>:8080

# 4. Check DNS
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never
nslookup <service-name>.<namespace>.svc.cluster.local
```

### Storage Issues

**Symptom: Persistent Volume Claim stuck in Pending**

```bash
# 1. Check PVC status
kubectl describe pvc <pvc-name> -n <namespace>

# 2. Check PV availability
kubectl get pv

# 3. Check storage class
kubectl get storageclass

# 4. Create PV if needed
# Or check storage backend health
```

---

## Emergency Procedures

### Cluster Failure Recovery

**Scenario: Control plane node failure**

```bash
# 1. Assess situation
kubectl get nodes

# 2. If HA setup, check other control planes
kubectl get cs

# 3. If single control plane:
#    - Bring failed node back online
#    - Or promote a worker to control plane

# 4. Verify cluster recovery
kubectl get nodes
kubectl get pods -A --field-selector=status.phase!=Running
```

**Scenario: etcd data corruption**

```bash
# 1. Stop Kubernetes components
sudo systemctl stop kubelet
sudo systemctl stop kube-apiserver

# 2. Restore from backup
sudo /var/backups/kubernetes/restore-etcd.sh

# 3. Start Kubernetes components
sudo systemctl start kube-apiserver
sudo systemctl start kubelet

# 4. Verify cluster health
kubectl get nodes
kubectl get pods -A
```

### Data Recovery

**Scenario: Accidental deletion of resources**

```bash
# 1. Check if resources are in Trash/Finalizers
kubectl get all -A --include-uninitialized

# 2. Check etcd backup for recovery point
ls -lh /var/backups/kubernetes/etcd/

# 3. If recoverable, restore from backup
sudo /var/backups/kubernetes/restore-etcd.sh --timestamp="<backup-time>"

# 4. Verify restoration
kubectl get <resource-type>
```

**Scenario: Accidental data deletion from persistent volume**

```bash
# 1. Check volume backup
ls -lh /var/backups/kubernetes/volumes/

# 2. Create recovery pod
kubectl run recovery-pod --image=alpine -n production -- sleep 3600

# 3. Mount volume and restore
kubectl exec -it recovery-pod -n production -- sh
# Mount volume
# Restore from backup files

# 4. Verify restoration
kubectl logs -n production deployment/<app>

# 5. Cleanup recovery pod
kubectl delete pod recovery-pod -n production
```

---

## Rollback Procedures

### Application Rollback

```bash
# 1. Check deployment history
kubectl rollout history deployment/<app> -n production

# 2. Rollback to previous version
kubectl rollout undo deployment/<app> -n production

# 3. Verify rollback
kubectl rollout status deployment/<app> -n production

# 4. Check application is working
kubectl logs deployment/<app> -n production
curl http://<app-endpoint>
```

### Configuration Rollback

```bash
# 1. Check ConfigMap history
kubectl get configmap -n production
kubectl describe configmap <config-name> -n production

# 2. Restore previous ConfigMap
kubectl delete configmap <config-name> -n production
kubectl apply -f /path/to/backup/configmap-backup.yaml

# 3. Restart pods to pick up changes
kubectl rollout restart deployment/<app> -n production

# 4. Verify configuration
kubectl exec deployment/<app> -n production -- env | grep CONFIG
```

---

## Support & Escalation

### Getting Help

**For Kubernetes Issues:**
```bash
# Check cluster events
kubectl get events -A --sort-by='.lastTimestamp'

# Check component logs
kubectl logs -n kube-system -l component=kubelet

# Check API server logs
kubectl logs -n kube-system -l component=kube-apiserver
```

**For Application Issues:**
```bash
# Check application logs
kubectl logs deployment/<app> -n production

# Check application traces
# Visit Jaeger: http://localhost:16686

# Check application metrics
# Visit Grafana: http://localhost:3000
```

**For Network Issues:**
```bash
# Test service connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never

# Check network policies
kubectl get networkpolicy -A

# Check DNS resolution
nslookup <service>.<namespace>.svc.cluster.local
```

---

## Contact Information

- **On-Call Engineer:** [Contact Info]
- **Escalation:** [Contact Info]
- **Emergency Line:** [Contact Info]
- **Documentation:** [Link to docs]
- **Incident Channel:** [Slack/Teams]

---

**Framework Status:** Production-Ready
**Last Reviewed:** November 17, 2025
**Next Review Date:** December 17, 2025
