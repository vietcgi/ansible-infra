# Capacity Planning Guide

## Current Capacity

### Infrastructure
- Hosts: 5-10 (scaling ready)
- Storage: 500 GB available (80% threshold)
- Network bandwidth: 1 Gbps available
- Backup storage: 2 TB allocated

### Growth Forecasting
- Monthly growth rate: [TBD - monitor]
- Scaling triggers: Disk 85%, CPU > 80% sustained
- Capacity review: Quarterly

## Scaling Procedures

### Horizontal Scaling (Add Hosts)
1. Provision new host with Ansible
2. Add to inventory
3. Apply configuration via Ansible
4. Monitor for 24 hours

### Vertical Scaling (More Resources)
1. Resize existing host
2. Verify services stable
3. Update monitoring thresholds
4. Document changes

---

**Last Updated**: November 15, 2025
