# Dependency Scanning & Supply Chain Security

## Dependency Types

### Ansible Collections
- **Primary**: grafana.grafana, prometheus.prometheus
- **Scanning**: Quarterly for CVEs
- **Updates**: Within 30 days of availability

### System Packages
- **Scanning**: Continuous (GitHub Dependabot)
- **Security updates**: Within 24 hours critical, 7 days others
- **Major updates**: Staged through environments

### Python Dependencies
- **Scanning**: pip-audit, safety weekly
- **Location**: requirements.txt
- **Action**: Update or document exceptions

### Ansible Version
- **Current**: 2.10+
- **Update strategy**: Quarterly review, test in staging first
- **Breaking changes**: Evaluated before upgrade

## Software Bill of Materials (SBOM)

Maintained in `dependencies/SBOM.md`:
- Ansible version
- All collections with versions
- Key system packages
- Python packages (if any)
- Last updated date

## Vulnerability Response

**On CVE discovery**:
1. Assess impact on ansible-infra
2. If critical: Emergency patch within 24 hours
3. If high: Patch within 7 days
4. If medium: Patch within 30 days
5. If low: Patch at next update cycle

## Pre-Deployment Checks

```bash
# Before merging to main
- ansible-lint passes (includes security rules)
- No new high/critical CVEs in dependencies
- All versions pinned
- SBOM updated
```

---

**Last Updated**: November 15, 2025
