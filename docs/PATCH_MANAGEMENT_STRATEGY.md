# Patch Management Strategy

## Patch Categories

### Critical
- **CVSS**: 9.0-10.0
- **Response time**: Within 24 hours
- **Approval**: Emergency fast-track
- **Testing**: Minimal (smoke tests)
- **Example**: Remote code execution vulnerability

### High
- **CVSS**: 7.0-8.9
- **Response time**: Within 7 days
- **Approval**: Manager approval
- **Testing**: Full test suite
- **Example**: Privilege escalation, authentication bypass

### Medium
- **CVSS**: 4.0-6.9
- **Response time**: Within 30 days
- **Approval**: Team lead
- **Testing**: Staging + smoke tests
- **Example**: Information disclosure, limited DoS

### Low
- **CVSS**: 0.1-3.9
- **Response time**: Within 90 days
- **Approval**: Self-approval
- **Testing**: Linting only
- **Example**: Documentation errors, minor bugs

## Patch Sources

- **Operating System**: Automatic security updates enabled
- **Ansible**: Quarterly review and update
- **Collections**: Quarterly review, security fixes within 7 days
- **Python packages**: Dependency scanning automated

## Patching Process

1. **Identify**: CVE alert or scheduled update
2. **Assess**: Impact on ansible-infra
3. **Develop**: Create patch/update
4. **Test**: Molecule tests for all patches
5. **Approve**: Manager approval (if required)
6. **Deploy**: Via change management process
7. **Verify**: Smoke tests and monitoring
8. **Document**: Update CHANGELOG

---

**Last Updated**: November 15, 2025
