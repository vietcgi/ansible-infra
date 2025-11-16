# Security Policy

## Overview

This document outlines the security practices, vulnerability disclosure procedures, and security controls for the ansible-infra project. We take security seriously and appreciate the community's help in identifying and responsibly disclosing vulnerabilities.

---

## Reporting Security Vulnerabilities

### IMPORTANT: DO NOT OPEN PUBLIC ISSUES FOR SECURITY VULNERABILITIES

If you discover a security vulnerability in ansible-infra, **please do NOT create a public issue or pull request**. Public disclosure can allow attackers to exploit the vulnerability before a fix is available.

### Responsible Disclosure Process

1. **Email Report**
   - Send vulnerability details to: `security@ansible-infra.local`
   - Include: CVE ID (if known), affected component, severity assessment, proof-of-concept
   - Subject line format: `[SECURITY] Vulnerability in [Component]: [Brief Description]`

2. **Response Timeline**
   - **Acknowledgment**: Within 48 hours
   - **Initial assessment**: Within 5 business days
   - **Fix development**: Within 14 calendar days for critical issues
   - **Release**: Within 30 days for critical, 60 days for high, 90 days for medium/low

3. **Coordination**
   - You may be asked to provide additional technical details
   - We will keep you informed of remediation progress
   - Credit will be given in security advisory (unless you request anonymity)
   - Embargo period: Recommended 90 days from fix release

### Vulnerability Severity Classification

We use CVSS v3.1 base scores for severity assessment:

| Severity | CVSS Score | Examples | Response Time |
|----------|-----------|----------|----------------|
| **Critical** | 9.0-10.0 | Remote code execution, complete system compromise | 24-48 hours |
| **High** | 7.0-8.9 | Authentication bypass, privilege escalation, data disclosure | 5-7 days |
| **Medium** | 4.0-6.9 | Information disclosure, denial of service, configuration issues | 14-30 days |
| **Low** | 0.1-3.9 | Documentation issues, minor configuration problems | As scheduled |

---

## Security Controls & Hardening

### 1. Infrastructure Hardening

#### SSH Security (roles/common/tasks/ssh_hardening.yml)
- **Post-quantum cryptography**: sntrup761x25519-sha512 key exchange (quantum-resistant)
- **Key algorithms**: Ed25519 (recommended), ECDSA, RSA 4096-bit minimum
- **Authentication**: Key-based only, password authentication disabled
- **Protocol**: SSH v2 only, no legacy protocols
- **Ciphers**: AES-GCM variants (authenticated encryption)
- **Configuration**: Restrictive sshd_config (0600 permissions)

#### System Hardening (31+ Controls)
- **Kernel parameters**: sysctl hardening for network and memory
- **File permissions**: Restrictive defaults, principle of least privilege
- **Audit logging**: auditd rules for system activity tracking
- **Time synchronization**: NTP for accurate logging timestamps
- **Package management**: Regular updates and security patches
- **DNS hardening**: Resolver configuration with security focus

### 2. Secrets Management

#### Ansible Vault
- **Usage**: All sensitive data encrypted with Ansible Vault
- **Encryption**: AES-256-CTR with PBKDF2 key derivation
- **Storage**: Vault files in inventories/*/vault/ directories
- **Key management**:
  - Never commit vault passwords to git
  - Use environment variable: `ANSIBLE_VAULT_PASSWORD_FILE`
  - Rotate keys periodically (quarterly minimum)
- **Access control**: Restrict vault file permissions (0600)

#### External Secret Management (Recommended)
- **HashiCorp Vault**: For dynamic secrets and credential rotation
- **AWS Secrets Manager**: For AWS-hosted deployments
- **Azure Key Vault**: For Azure-hosted deployments
- **Implementation**: Use Ansible Vault plugin integration

### 3. Access Control

#### Role-Based Access Control (RBAC)
- **Ansible execution**: Use dedicated service accounts
- **Privilege escalation**: Minimal required privileges
- **Audit trail**: All Ansible executions logged with timestamps
- **Approval workflow**: Changes above severity threshold require approval

#### SSH Access Control
- **Key management**: Individual keys per user, never shared
- **Key rotation**: Annual rotation minimum
- **Access revocation**: Immediate removal of departed team members
- **Bastion hosts**: For production environment access

### 4. Compliance Mappings

#### NIST SP 800-219 (Cybersecurity Maturity Model Certification)
- **AC-2**: Account Management - Service account controls implemented
- **AC-3**: Access Enforcement - RBAC implemented via Ansible roles
- **AU-2**: Audit Events - Audit daemon logging configured
- **CM-3**: Access Restrictions for Change - Change approval process defined
- **SC-4**: Information in Shared Resources - File permissions restrictive
- **SC-7**: Boundary Protection - Network segmentation via inventories

#### CIS Benchmarks
- **CIS Ubuntu Linux**: Post-quantum SSH, sysctl hardening, audit rules
- **CIS Debian Linux**: Similar controls to Ubuntu
- **CIS RedHat**: Additional controls for RHEL/Rocky/CentOS
- **CIS Controls**: Prioritized asset management, inventory, access control

#### NIST Cybersecurity Framework
- **Identify**: Asset inventory, vulnerability scanning with ansible-lint
- **Protect**: SSH hardening, access control, secret encryption
- **Detect**: Audit logging, NTP synchronization
- **Respond**: Incident response procedures documented
- **Recover**: Backup and disaster recovery procedures

### 5. Code Security

#### Linting & Static Analysis
- **ansible-lint**: Production profile enabled, rules enforced in CI
- **Pre-commit hooks**: Run linting before commits
- **Code review**: All changes require review before merge
- **Branch protection**: main/master branch protected, requires checks

#### Dependency Management
- **Ansible version**: Pinned in requirements (minimum 2.10)
- **Collection versions**: Pinned in requirements.yml
- **Role dependencies**: Explicit version specifications
- **Supply chain security**: Regular dependency scanning for vulnerabilities
- **SBOM**: Software Bill of Materials maintained in dependencies/SBOM.md

#### Cryptography
- **SSH keys**: Strong key types only (Ed25519 preferred)
- **TLS/SSL**: Modern protocols, strong ciphers
- **Password hashing**: bcrypt with high work factors
- **Random generation**: OS-provided entropy sources

---

## Security Best Practices

### Development

1. **Code Review**
   - All changes require at least 2 approvals
   - Security reviewers must review changes touching sensitive areas
   - Use GitHub's code review tools for discussion and approval

2. **Testing**
   - Molecule tests on 4 platforms before merge
   - Integration tests for critical components
   - Security scanning in CI pipeline

3. **Commit Messages**
   - Include security implications if relevant
   - Reference security issues with [SECURITY] prefix
   - Link to vulnerability tracking system

### Deployment

1. **Pre-deployment Checklist**
   - Vault credentials securely configured
   - Change management approval obtained
   - Rollback plan documented
   - Backup taken before critical changes

2. **Execution Logging**
   - All playbook runs logged with timestamp, user, changes
   - Log retention: Minimum 1 year for critical systems
   - Log protection: Immutable storage, access-controlled

3. **Verification**
   - Smoke tests after deployment
   - Configuration verification
   - Health checks passing
   - Monitoring alerts within expected ranges

### Incident Response

1. **Detection**
   - Monitoring alerts configured for security events
   - Log analysis for suspicious activity
   - Automated alerting for critical events

2. **Containment**
   - Identify affected systems immediately
   - Isolate if necessary (disable access, reset credentials)
   - Preserve evidence for post-mortem

3. **Recovery**
   - Follow disaster recovery procedures
   - Restore from clean backups if compromised
   - Verify integrity of restored systems

4. **Post-Incident**
   - Document incident details in incident report template
   - Conduct post-mortem with team
   - Implement corrective actions
   - Update security policies as needed

---

## Supply Chain Security

### Dependency Management

1. **Ansible Collections**
   - Verified checksums from Ansible Galaxy
   - Version pinning in requirements.yml
   - Regular audits for deprecated or unmaintained collections

2. **Community Roles**
   - Evaluate trust level and maintenance status
   - Review for security issues before adoption
   - Pin to stable versions

3. **System Packages**
   - Repository trust validation
   - Signature verification where available
   - Security update automation for critical packages

### Vulnerability Scanning

1. **Dependencies**
   - Regular scans with tools like `pip-audit`, `safety`
   - CVE monitoring via security advisories
   - Automated alerts for new vulnerabilities

2. **Code**
   - ansible-lint in production profile
   - Static security analysis
   - Credentials scanning (detect-secrets, git-secrets)

3. **System**
   - OS vulnerability scanning
   - Compliance checking
   - Configuration validation

---

## Security Incident Timeline & Response

### Critical Severity (CVSS 9.0-10.0)
```
Report Received
    ↓ (within 48 hours)
Vulnerability Confirmed
    ↓ (within 24 hours)
Fix Development Begins
    ↓ (within 14 days)
Patch Testing Complete
    ↓ (within 21 days)
Release Security Advisory & Fix
    ↓ (notify users immediately)
Users Apply Fix
    ↓ (target: 24 hours)
Incident Closed
```

### High Severity (CVSS 7.0-8.9)
```
Report Received
    ↓ (within 48 hours)
Vulnerability Confirmed
    ↓ (within 5 business days)
Fix Development & Testing
    ↓ (within 14 days)
Release Advisory & Fix
    ↓ (notify users)
Incident Closed
```

### Medium/Low Severity (CVSS <7.0)
```
Report Received
    ↓ (within 1 week)
Assessment & Planning
    ↓ (within 30 days)
Fix Release
    ↓ (if applicable)
Incident Closed
```

---

## Audit & Monitoring

### Continuous Monitoring

1. **System Logs**
   - Centralized log collection to /var/log/ansible-infra/
   - Log aggregation with ELK or Loki
   - Real-time alerting for security events

2. **Metrics**
   - Prometheus metrics for system health
   - Grafana dashboards for visualization
   - SLA/SLO tracking

3. **Audit Trail**
   - All administrative actions logged
   - Ansible execution logging with user context
   - Configuration change tracking

### Regular Assessments

1. **Security Audits**
   - Quarterly internal audits
   - Annual third-party penetration testing
   - Post-incident reviews

2. **Compliance Audits**
   - NIST compliance validation
   - CIS benchmark assessment
   - Policy enforcement verification

3. **Vulnerability Assessments**
   - Quarterly dependency scans
   - Annual OS vulnerability assessments
   - Code security reviews

---

## Security Updates & Patches

### Patch Management Strategy

1. **Identification**
   - Monitor security advisories daily
   - Subscribe to vendor security lists
   - Track CVE databases

2. **Prioritization**
   - Critical: Apply within 24 hours
   - High: Apply within 7 days
   - Medium: Apply within 14 days
   - Low: Apply within 30 days

3. **Testing**
   - Test patches in staging environment
   - Run Molecule test suite
   - Verify no breaking changes

4. **Deployment**
   - Approved patches deployed via standard change process
   - Coordinated rollout to minimize risk
   - Verification and rollback plan ready

### Auto-Updates

1. **Security Packages**
   - Automatic security updates recommended
   - Manual review before OS updates
   - Critical package monitoring

2. **Collections/Dependencies**
   - Manual review process for updates
   - Staged rollout to test environments first
   - Automated alerts for vulnerable versions

---

## Responsible Disclosure Examples

### Example 1: Remote Code Execution
```
Subject: [SECURITY] Remote Code Execution in SSH configuration
Impact: High
Affected: roles/common (all versions)
CVSS: 8.5

Description: Ansible template injection allows arbitrary command execution
through crafted variable input in sshd_config generation.

POC: [Detailed proof of concept provided]
Recommended fix: [Specific template fix]
```

### Example 2: Information Disclosure
```
Subject: [SECURITY] Vault password exposure in logs
Impact: Medium
Affected: ansible-infra (all versions)
CVSS: 6.2

Description: Vault password variables logged in plaintext to Ansible logs
when verbose output enabled.

POC: [Steps to reproduce]
Recommended fix: [Specific logging fix]
```

---

## Contact

For security issues, contact: `security@ansible-infra.local`

For non-security issues, use: [GitHub Issues](https://github.com/ansible/ansible-infra/issues)

For documentation questions, use: [GitHub Discussions](https://github.com/ansible/ansible-infra/discussions)

---

## Policy Updates

This security policy is reviewed quarterly and updated as needed. Last updated: **November 15, 2025**

**Version**: 1.0.0
**Status**: Active
**Next Review**: February 15, 2026
