# Architecture Decision Records (ADRs)

## ADR Template

```
# ADR-XXX: [Decision Title]

**Date**: [YYYY-MM-DD]
**Status**: [Proposed/Accepted/Deprecated]
**Context**: [Why we needed to make this decision]
**Decision**: [What we decided to do]
**Consequences**: [Positive and negative impacts]
**Alternatives Considered**: [Other options evaluated]
**References**: [Related issues, RFCs, etc.]
```

---

## Current ADRs

### ADR-001: Use Ansible for Infrastructure Automation

**Status**: Accepted
**Date**: 2024-01-01

**Context**: Need agentless infrastructure automation
**Decision**: Use Ansible (agentless, YAML-based, widely adopted)
**Consequences**:
- ✓ No agent required
- ✓ Simple learning curve
- ✗ No built-in state management

---

### ADR-002: Multi-Platform Support Strategy

**Status**: Accepted
**Date**: 2024-06-01

**Context**: Support Linux and macOS
**Decision**: Single Ansible common role for Linux, separate role for macOS
**Consequences**:
- ✓ Leverages Ansible collections for Linux
- ✓ Custom role for macOS specifics
- ✗ Code duplication possible

---

### ADR-003: Post-Quantum Cryptography

**Status**: Accepted
**Date**: 2025-01-01

**Context**: Future-proof against quantum computing threats
**Decision**: Use sntrup761x25519 hybrid key exchange in SSH
**Consequences**:
- ✓ Quantum-resistant
- ✓ Backward compatible
- ✗ Requires modern OpenSSH (7.4+)

---

## Process for New ADRs

1. Open issue describing decision
2. Discuss alternatives as a team
3. Reach consensus
4. Document in this file
5. Implement and track consequences

---

**Last Updated**: November 15, 2025
