# Performance Benchmarks

## Baseline Metrics

### Playbook Execution
- Provision playbook: 12-15 minutes
- Configure playbook: 3-5 minutes
- Maintenance playbook: 8-10 minutes

### Configuration Convergence
- Single role application: 1-2 minutes
- Full host configuration: 3-5 minutes
- Idempotent re-run: 45-60 seconds

### SSH Performance
- Connection time: < 2 seconds
- Authentication time: 500-800ms
- Key exchange time: 100-150ms

### Resource Usage
- Memory (idle): 512 MB
- Memory (active): 1-2 GB
- CPU (idle): < 5%
- CPU (active): 20-40%
- Disk I/O: < 50 MB/s

---

**Last Updated**: November 15, 2025
