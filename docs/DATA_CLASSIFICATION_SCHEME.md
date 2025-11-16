# Data Classification Scheme

## Classification Levels

### Public (Level 1)
- **Definition**: No confidentiality impact if disclosed
- **Examples**: Documentation, README files, public APIs
- **Protection**: Integrity only (checksums)
- **Access**: Anyone

### Internal (Level 2)
- **Definition**: Confidential to organization
- **Examples**: Runbooks, internal policies, architecture
- **Protection**: Encryption recommended, access-controlled
- **Access**: Employees only

### Confidential (Level 3)
- **Definition**: Sensitive business information
- **Examples**: Customer data, metrics, configurations
- **Protection**: Encryption required, minimal access
- **Access**: Need-to-know basis

### Restricted (Level 4)
- **Definition**: Highly sensitive, regulatory impact
- **Examples**: SSH keys, passwords, secrets, PII
- **Protection**: Encryption + access control, audit logging
- **Access**: Minimal, with approval

## Data Handling by Classification

| Level | Storage | Transmission | Access | Retention |
|-------|---------|--------------|--------|-----------|
| Public | Plain | HTTP | Open | Indefinite |
| Internal | Plain | HTTPS | Employees | 1 year |
| Confidential | Encrypted | HTTPS | Restricted | 90 days |
| Restricted | Vault | TLS 1.3 | Minimal | Per policy |

---

**Last Updated**: November 15, 2025
