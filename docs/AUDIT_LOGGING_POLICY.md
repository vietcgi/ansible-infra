# Audit Logging Policy

## Log Types

### Access Logs
- SSH logins (user, host, time, success/failure)
- Vault access (who accessed what secret)
- API calls (to monitoring/management systems)

**Retention**: 1 year
**Access**: Security team only

### Change Logs
- Ansible playbook executions
- Configuration modifications
- Infrastructure provisioning

**Retention**: 2 years
**Access**: Operations team

### Incident Logs
- Incident creation and resolution
- Escalation events
- Post-mortem notes

**Retention**: 3 years (compliance)
**Access**: Management + incident participants

### Compliance Logs
- Policy changes
- Access control modifications
- Security events

**Retention**: 3 years minimum
**Access**: Compliance officer + security team

## Log Format

All logs include:
- Timestamp (ISO 8601)
- User/service performing action
- Action taken
- Resource affected
- Result (success/failure)
- Reason (if applicable)

**Example**:
```
2025-11-15T14:23:45.123Z alice SSH ssh-ed25519 AAAAC3... success key-based authentication
2025-11-15T14:24:12.456Z alice ANSIBLE provision.yml started duration 23m status success
```

## Log Monitoring

- Real-time alerts for security events
- Weekly log review
- Monthly log archival
- Quarterly audit

---

**Last Updated**: November 15, 2025
