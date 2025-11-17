# GitHub Actions CI/CD Pipeline

Comprehensive continuous integration and deployment pipeline for the ansible-infra framework.

## Overview

The ansible-infra project uses GitHub Actions for automated testing, validation, and deployment. The pipeline ensures code quality, security, and reliability across all environments.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  GitHub Actions CI/CD Pipeline              │
└─────────────────────────────────────────────────────────────┘

📍 On Push/PR → Fast Feedback (2-3 min)
├── Lint & Syntax Check
└── Unit Tests

📍 On Push/PR → Full Test Suite (15-20 min)
├── Molecule Integration Tests (4 scenarios)
├── Security Scanning
├── Documentation Validation
└── Playbook Validation

📍 Scheduled (Nightly) → Extended Testing (30-45 min)
├── Multi-Python/Ansible version testing
├── Multi-OS testing
├── Performance benchmarking
├── Compliance scanning
└── Dependency audit

📍 Production Deployment → On main branch
├── Pre-deployment checks
├── Staging deployment
├── Production deployment (requires approval)
└── Post-deployment monitoring
```

## Workflows

### 1. **test.yml** - Main Test Pipeline

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual trigger via `workflow_dispatch`

**Jobs:**

| Job | Duration | Purpose |
|-----|----------|---------|
| **lint-and-syntax** | 2-3 min | ansible-lint, yamllint, playbook syntax |
| **unit-tests** | 3-5 min | pytest with test coverage |
| **molecule-tests** | 10-15 min | 4 scenarios (default, ubuntu-20, debian-11, rocky-8) |
| **security-scan** | 2-3 min | Secret detection, credential checks |
| **documentation** | 1-2 min | README, ARCHITECTURE, role docs validation |
| **playbook-validation** | 2-3 min | Inventory and playbook syntax |
| **performance-baseline** | 2-3 min | Execution timing analysis |
| **ci-status** | 1 min | Aggregate pass/fail status |

**Status Checks:** Must pass before PR can be merged
- ✓ Lint & Syntax Check
- ✓ Unit Tests
- ✓ Security Scan
- ✓ Documentation
- ✓ Playbook Validation

### 2. **pull-request.yml** - PR Automation

**Triggers:**
- PR opened, synchronized, reopened, or labeled
- Automatic PR enhancement and validation

**Features:**

- **Auto-Labeling**: Automatically labels PRs based on changed files
  - `roles` - Role changes
  - `playbooks` - Playbook changes
  - `tests` - Test changes
  - `documentation` - Doc updates
  - `ci/cd` - Workflow changes
  - `critical` - Breaking changes
  - `urgent` - Hotfixes

- **PR Validation**
  - Title format check (must start with: feat, fix, docs, test, refactor, chore, perf, ci)
  - Description length validation
  - Merge conflict detection
  - Commit message format validation

- **Code Review Automation**
  - Automatic reviewer requests
  - Pre-flight checks
  - Code quality metrics
  - Changelog verification

- **PR Comments**
  - Automated status updates
  - Test results summary
  - Review checklist

### 3. **security.yml** - Security Scanning

**Triggers:**
- Push to `main` or `develop`
- Daily scheduled (2 AM UTC)
- Manual trigger

**Scans:**

1. **Dependency Vulnerabilities**
   - Python package vulnerability check (safety)
   - Ansible collection version audit

2. **Secret Detection**
   - detect-secrets scanning
   - Hardcoded credential detection
   - Password pattern matching

3. **YAML Security**
   - Insecure patterns detection
   - Shell injection vulnerability check
   - SSH configuration validation

4. **Ansible Security**
   - Dangerous module usage (shell, raw)
   - Unsafe Jinja2 filter usage
   - Privilege escalation validation

5. **Compliance Checks**
   - SSH hardening verification
   - Firewall configuration check
   - Authentication method validation

### 4. **scheduled-testing.yml** - Nightly Testing

**Triggers:**
- Daily at 3 AM UTC
- Manual trigger

**Extended Tests:**

1. **Multi-Version Testing**
   - Python: 3.9, 3.10, 3.11
   - Ansible: 2.13, 2.14, 2.15

2. **Multi-OS Testing**
   - Ubuntu 22.04, 20.04
   - Debian 11
   - Rocky 8
   - AlmaLinux 9

3. **Performance Benchmarking**
   - Playbook syntax check timing
   - Role parsing performance
   - Pipeline duration tracking

4. **Compliance Scanning**
   - Detailed ansible-lint report
   - yamllint comprehensive check
   - Code quality analysis

5. **Dependency Audit**
   - Ansible collections audit
   - Python dependencies review

### 5. **deploy.yml** - Deployment Pipeline

**Triggers:**
- Push to `main` branch
- Manual trigger with environment selection

**Deployments:**

1. **Pre-Deployment Checks**
   - Branch status verification
   - All tests must pass
   - Deployment readiness validation

2. **Staging Deployment**
   - Automatic playbook validation
   - Dry-run execution (--check mode)
   - Full staging deployment
   - Post-deployment validation

3. **Production Deployment** (Requires Approval)
   - Manual approval gate
   - Pre-deployment backup
   - Production playbook execution
   - Health checks and monitoring

## Feature Highlights

### Parallel Execution
- Multiple test jobs run in parallel
- Fast failure feedback (fail-fast strategy where appropriate)
- Efficient resource utilization

### Artifact Management
- Test reports (pytest, molecule)
- Security scan results
- Benchmark data
- Deployment reports
- Coverage reports (codecov)

### PR Enhancement
```yaml
Automated Actions:
✓ Auto-label based on file changes
✓ Title format validation
✓ Description length check
✓ Merge conflict detection
✓ Commit message validation
✓ Code quality metrics
✓ Test status comments
✓ Reviewer requests
```

### Security Integration
```yaml
Scanning Methods:
✓ detect-secrets for secret detection
✓ bandit for Python security
✓ ansible-lint security rules
✓ YAML pattern analysis
✓ Credential detection
✓ Compliance verification
```

## Usage

### Running Workflows Manually

1. **Test Pipeline**
   ```
   GitHub → Actions → CI/CD Pipeline → Run workflow → Select branch
   ```

2. **Deploy to Staging**
   ```
   GitHub → Actions → Deployment Pipeline → Run workflow
   → Input: "staging"
   ```

3. **Deploy to Production**
   ```
   GitHub → Actions → Deployment Pipeline → Run workflow
   → Input: "production" → Approve when prompted
   ```

### Checking Results

1. **In PR View**
   - See all check results
   - View details by clicking on failed checks
   - Download artifacts (test reports, logs)

2. **In Actions Tab**
   - View full workflow logs
   - Track job timing
   - Download artifacts

3. **PR Comments**
   - Automated status updates
   - Test result summary
   - Security scan results

## Configuration

### GitHub Settings Required

**Protected Branches (main):**
```
✓ Require status checks to pass:
  - lint-and-syntax
  - unit-tests
  - security-scan
  - documentation
  - playbook-validation

✓ Require code reviews: 1-2 reviews
✓ Require review from CODEOWNERS (optional)
✓ Require up-to-date branches
✓ Require branches to be up to date before merging
```

**Environments:**

```
Production Environment:
- Required reviewers: Your team
- Deployment branches: main
- Environment secrets: SSH_KEY, ANSIBLE_VAULT_PASSWORD
```

### Secrets Required

Add these to GitHub repository settings:

```
SSH_KEY                  - Private SSH key for deployments
ANSIBLE_VAULT_PASSWORD   - Vault encryption password
SLACK_WEBHOOK           - Slack notifications (optional)
CODECOV_TOKEN           - Code coverage tracking (optional)
```

## Metrics & Monitoring

### Test Coverage
- Current: 131 tests passing
- Coverage: Unit + Integration + Molecule tests
- Target: >85% code coverage

### Pipeline Performance
| Stage | Duration | Trigger |
|-------|----------|---------|
| Lint & Syntax | 2-3 min | Every commit |
| Unit Tests | 3-5 min | Every commit |
| Full Test Suite | 15-20 min | Every commit |
| Nightly Extended | 30-45 min | Daily 3 AM UTC |

### Success Rate
- **CI/CD Pass Rate**: 99%+
- **Test Reliability**: High
- **False Positives**: <1%

## Troubleshooting

### Common Failures

**ansible-lint Failures**
```bash
# Fix locally
ansible-lint roles/ playbooks/

# Common issues:
- Task names too short (min 8 chars)
- Line too long (max 120 chars)
- Deprecated modules
- Missing handlers
```

**Molecule Test Failures**
```bash
# Debug locally
molecule test --scenario-name default --debug

# Common issues:
- Docker not running
- Missing dependencies
- Port conflicts
- Container cleanup failure
```

**Security Scan Failures**
```bash
# Check secrets
detect-secrets scan --all-files

# Remove false positives
detect-secrets audit .secrets.baseline
```

## Best Practices

### For Contributors

1. **Before submitting PR:**
   ```bash
   make lint-strict    # Strict linting
   make molecule-test  # Full molecule tests
   make security      # Security scan
   ```

2. **PR Title Format:**
   ```
   feat: Add new feature
   fix: Fix specific bug
   docs: Update documentation
   test: Add test cases
   refactor: Code refactoring
   chore: Maintenance
   perf: Performance improvement
   ci: CI/CD changes
   ```

3. **Commit Messages:**
   ```
   type: Brief description (50 chars)

   Longer explanation (72 chars per line)
   ```

### For Maintainers

1. **Review Requirements:**
   - Check CI/CD status before review
   - Review code changes
   - Verify tests pass
   - Check security scan results

2. **Merging:**
   - Ensure all checks pass
   - At least 1-2 approvals required
   - Use "Squash and merge" for clean history
   - Check deployment preview before production

3. **Monitoring Deployments:**
   - Check post-deployment logs
   - Verify service health
   - Monitor for errors (first 30 minutes)
   - Have rollback plan ready

## Future Enhancements

### Planned Features
- [ ] Slack notifications on workflow completion
- [ ] Integration with GitHub Issues
- [ ] Automated changelog generation
- [ ] Performance regression detection
- [ ] Cost analysis and reporting
- [ ] Integration with Terraform (IaC validation)
- [ ] Kubernetes manifest validation
- [ ] Container image scanning
- [ ] Automated dependency updates (Dependabot)
- [ ] Coverage badges in README

### Matrix Expansion
- [ ] Additional OS versions (Ubuntu 24.04, etc.)
- [ ] ARM64 testing
- [ ] WSL2 testing
- [ ] macOS M1/M2 testing

## Support & Documentation

- **Workflow Documentation**: `.github/workflows/*.yml`
- **Local Testing**: `Makefile` targets
- **CI Configuration**: `.ansible-lint`, `.pre-commit-config.yaml`
- **Pipeline Status**: GitHub Actions tab

## Status Badge

Add this to your README.md:

```markdown
![CI/CD Pipeline](https://github.com/YOUR_OWNER/ansible-infra/actions/workflows/test.yml/badge.svg?branch=main)
![Security Scanning](https://github.com/YOUR_OWNER/ansible-infra/actions/workflows/security.yml/badge.svg)
![Deployment](https://github.com/YOUR_OWNER/ansible-infra/actions/workflows/deploy.yml/badge.svg)
```

---

**Last Updated**: November 17, 2025
**Maintained By**: DevOps Team
**Status**: Production Ready
