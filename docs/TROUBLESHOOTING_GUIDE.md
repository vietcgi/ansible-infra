# Troubleshooting Guide

## Common Issues

### SSH Connection Refused
**Symptoms**: Cannot SSH to host
**Causes**: 
- SSH service not running
- Firewall blocking
- Wrong key
- Network issue

**Resolution**:
1. Check host reachable: `ping host`
2. Check SSH running: `ansible host -m systemd -a "name=ssh"`
3. Check firewall: `ansible host -m firewalld -a "port=22"`
4. Verify key: `ssh-keygen -l -f ~/.ssh/id_ed25519`

### High Disk Usage
**Symptoms**: Disk full, no space errors
**Causes**:
- Old logs not rotated
- Backups not cleaned
- Temp files accumulated

**Resolution**:
See Disk Space Recovery runbook in OPERATIONAL_RUNBOOKS.md

### Slow Playbook Execution
**Symptoms**: Playbook takes longer than usual
**Causes**:
- System resource constrained
- Network latency
- Lock contention

**Resolution**:
1. Check system resources: `top`, `df`, `netstat`
2. Identify slow task: Add `-vv` flag
3. Optimize task or parallelize
4. Check for locks: `lsof | grep .lock`

---

**Last Updated**: November 15, 2025
