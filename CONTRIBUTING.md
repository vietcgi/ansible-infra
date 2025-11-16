# Contributing to ansible-infra

Thank you for considering contributing to **ansible-infra**! This document provides guidelines and instructions for contributing to the project.

**Status**: ✅ Production-Ready | 🔒 Security-Focused | 🧪 Well-Tested

---

## Getting Started

### Prerequisites

- **Ansible** 2.15 or later
- **Python** 3.8 or later
- **Git** (for version control)
- **Make** (for automation commands)
- SSH access to test servers (for actual deployment testing)

### Development Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ansible-infra.git
cd ansible-infra

# Install dependencies
make install-dev

# Verify setup
make test-fast
```

### What to Install

```bash
# Core dependencies
make install          # Installs Ansible + collections

# Development tools
make install-dev      # Adds: molecule, pytest, ansible-lint, pre-commit, etc.

# Git hooks
make setup-hooks      # Installs pre-commit hooks for quality checks
```

---

## How to Contribute

### Types of Contributions

We welcome contributions in these areas:

#### 1. **Bug Reports & Fixes** ✅
- Report bugs via GitHub Issues with clear reproduction steps
- Submit PRs that fix identified issues
- Include tests demonstrating the fix

**Example Issue Title**: `Fix: SSH hardening fails on Rocky Linux 9`

#### 2. **Documentation** ✅
- Improve README, guides, or inline comments
- Fix typos or unclear explanations
- Add examples or tutorials
- Update compliance mappings

**Example PR Title**: `docs: clarify NTP configuration options`

#### 3. **New Features** ✅
- New role capabilities
- Additional security hardening controls
- Support for new operating systems
- Enhanced monitoring/observability

**Example Issue Title**: `feat: add support for Ubuntu 24.04 LTS`

#### 4. **Testing & Quality** ✅
- Add Molecule test scenarios
- Improve test coverage
- Fix linting/syntax issues
- Enhance CI/CD pipelines

**Example PR Title**: `test: add Molecule scenarios for common role`

#### 5. **Security Improvements** ⚠️ PRIORITY
- Report security issues privately (see [Security Policy](#security))
- Propose security control enhancements
- Update compliance mappings
- Improve cryptographic algorithms

**Example PR Title**: `security: add post-quantum SSH algorithms`

---

## Development Workflow

### 1. Find an Issue to Work On

```bash
# Browse open issues
# Look for labels: good-first-issue, help-wanted, enhancement, bug

# Good starting points:
# - Documentation improvements
# - Small bug fixes
# - Test coverage additions
```

**Labels Guide:**
- 🟢 `good-first-issue` - Perfect for beginners
- 🟡 `help-wanted` - Community contributions welcome
- 🔴 `bug` - Something isn't working
- 🟣 `enhancement` - New feature or improvement
- 🔵 `documentation` - Documentation updates
- ⚫ `security` - Security-related fix

### 2. Create a Feature Branch

```bash
# Create descriptive branch names
git checkout -b fix/ssh-hardening-rocky-9
git checkout -b feat/ubuntu-24-support
git checkout -b docs/clarify-ntp-config
git checkout -b test/add-molecule-scenarios

# Branch naming convention:
# - type/description-in-kebab-case
# - type: fix, feat, docs, test, refactor, chore
```

### 3. Make Your Changes

#### For Role Changes

**Task Files** (`roles/*/tasks/*.yml`):
```yaml
---
# Clear, descriptive name
- name: Configure SSH daemon with hardening
  template:
    src: sshd_config.j2
    dest: /etc/ssh/sshd_config
    backup: yes
    mode: '0600'
    validate: '/usr/sbin/sshd -t -f %s'  # Validate before applying
  become: yes
  notify: restart sshd
  when: ansible_os_family == "Debian"
  tags:
    - ssh
    - hardening
    - security
```

**Best Practices:**
- ✅ Use descriptive task names (minimum 8 characters)
- ✅ Add `when` conditions for OS-specific tasks
- ✅ Include `notify` for service restarts
- ✅ Add `validate` for config files when possible
- ✅ Add relevant tags for granular execution
- ✅ Use `backup: yes` for configuration changes
- ✅ Include comments for complex logic

**Template Files** (`roles/*/templates/*.j2`):
```jinja2
# {{ ansible_managed }}
# Clear description of what this template does

# Variables are properly escaped
Port {{ common_ssh_port }}
HostKey {{ item.path }}
{% for server in common_ntp_servers %}
server {{ server }}
{% endfor %}
```

**Defaults** (`roles/*/defaults/main.yml`):
```yaml
---
# Group related variables with comments
# System Updates
common_update_packages: true
common_upgrade_packages: true

# SSH Security (when to disable password auth, etc.)
common_ssh_port: 22
common_ssh_permit_root_login: "no"
common_ssh_password_authentication: "no"
```

#### For Documentation Changes

- Use clear, concise language
- Include code examples
- Reference relevant files/sections
- Add context about why (not just what)
- Update table of contents if adding sections

#### For Tests

- Add tests alongside changes
- Test multiple scenarios (if applicable)
- Verify idempotence (run twice)
- Test edge cases
- Document test scenarios

### 4. Test Your Changes Locally

```bash
# Syntax validation
make test-fast              # Quick: lint + syntax (2 min)

# Full test suite
make test                   # Complete: all tests (15 min)

# Molecule testing (for roles)
cd roles/system_hardening_macos
molecule test               # Full test lifecycle

# Specific role testing
make molecule-test          # Test all Molecule scenarios

# Playbook validation
ansible-playbook playbooks/provision.yml --syntax-check

# Dry-run on staging
ansible-playbook playbooks/provision.yml \
  -i inventories/staging/hosts.yml \
  --check --diff
```

### 5. Verify Code Quality

```bash
# Run linting
make lint                   # Check code style

# Security scanning
make security               # Scan for vulnerabilities

# Pre-commit checks
make setup-hooks            # Install hooks (prevents bad commits)
git commit -m "message"     # Hooks run automatically
```

**Pre-commit Checks (Automatic):**
- ✅ YAML syntax validation
- ✅ Ansible-lint checks
- ✅ Secret detection
- ✅ Trailing whitespace removal
- ✅ File size limits

### 6. Commit with Clear Messages

```bash
# Follow this format:
# <type>: <brief description>
#
# <optional detailed explanation>

# Examples:
git commit -m "fix: resolve SSH lockout on macOS Sonoma"
git commit -m "feat: add support for Ubuntu 24.04 LTS"
git commit -m "docs: clarify NTP server configuration"
git commit -m "test: add Molecule scenarios for common role"
git commit -m "refactor: simplify DNS configuration logic"

# Commit types:
# - feat: A new feature
# - fix: A bug fix
# - docs: Documentation changes
# - test: Adding or updating tests
# - refactor: Code changes without feature/fix
# - perf: Performance improvements
# - chore: Maintenance, dependencies
# - security: Security hardening
# - ci: CI/CD pipeline changes
```

**Commit Message Guidelines:**
- ✅ Use imperative mood ("add" not "added" or "adds")
- ✅ Don't capitalize first letter
- ✅ No period at end of subject line
- ✅ Keep subject under 50 characters
- ✅ Wrap body at 72 characters
- ✅ Reference issues: "Fixes #123"
- ❌ Avoid vague messages: "update stuff", "fix things"

---

## Creating a Pull Request

### Before Creating PR

- [ ] Branch is up-to-date: `git fetch origin && git rebase origin/main`
- [ ] All tests pass locally: `make test`
- [ ] Code follows project style: `make lint`
- [ ] No sensitive data in commits (check `.gitignore`)
- [ ] Commits are logical and well-organized
- [ ] One concern per PR (focused changes)

### PR Title & Description

**Title Format:**
```
<type>: <description>

Examples:
- fix: prevent SSH lockout on macOS
- feat: add post-quantum SSH algorithms
- docs: clarify role variable usage
```

**Description Template:**

```markdown
## Summary
Brief explanation of what this PR does.

## Changes
- Specific change 1
- Specific change 2
- Specific change 3

## Testing
How did you test these changes?
- [ ] Ran `make test-fast` - all pass
- [ ] Ran `make test` - all pass
- [ ] Tested on [OS/version]
- [ ] Verified idempotence (ran twice)

## Related Issues
Fixes #123
Related to #456

## Checklist
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Ready for review
```

### Push and Create PR

```bash
# Push your branch
git push origin fix/ssh-hardening-rocky-9

# Create PR via GitHub CLI
gh pr create --title "fix: SSH hardening fails on Rocky Linux 9" \
  --body "Fixes #123. Updates sshd config to handle Rocky-specific..."

# Or create via GitHub web interface
# Visit: https://github.com/your-org/ansible-infra/pulls
```

---

## Code Review Process

### Expectations

**For Contributors:**
- Be open to feedback
- Respond to comments within 2 days if possible
- Make requested changes in new commits (don't force-push after review starts)
- Test again after making changes
- Ask questions if requirements are unclear

**For Reviewers:**
- Provide constructive feedback
- Suggest improvements, don't demand
- Approve when quality standards are met
- Review within 3-5 days when possible

### Review Criteria

Code is approved when it meets these standards:

✅ **Functionality**
- Does what it claims to do
- Handles edge cases
- Fails gracefully

✅ **Quality**
- Follows project code style
- Uses existing patterns
- Clear and readable

✅ **Testing**
- Tests pass locally
- Tests added for changes
- Idempotent (safe to run multiple times)

✅ **Documentation**
- README/comments updated if needed
- Changes are clear to other developers
- Security implications noted

✅ **Security**
- No hardcoded secrets
- No privilege escalation issues
- Follows security best practices

### Responding to Review Comments

**Good Response:**
```
Thanks for catching that! You're right - I'll refactor the error
handling to match the pattern in ssh_hardening.yml. I'll push
that change shortly.
```

**Avoid:**
```
But that's how I write code...
I don't think that's necessary...
Everyone does it this way...
```

---

## Role Development Guidelines

### Common Role (Foundation)

**Purpose**: Multi-platform OS configuration (Debian, RedHat, macOS)

**Guidelines:**
- Validate OS compatibility first
- Support all three platform families
- Use `when: ansible_os_family == "X"` for OS-specific tasks
- Provide sensible defaults for all variables
- Document all variables in defaults/main.yml
- Test on Ubuntu, Debian, Rocky, and macOS

**Adding a New Task:**
1. Create `roles/common/tasks/new_task.yml`
2. Import in `tasks/main.yml` in correct order
3. Add variables to `defaults/main.yml`
4. Add to documentation
5. Test on multiple OS families

### Platform-Specific Roles (e.g., system_hardening_macos)

**Purpose**: OS-specific hardening and configuration

**Guidelines:**
- Focus on security controls
- Reference compliance standards (NIST, CIS)
- Provide granular configuration options
- Include comprehensive documentation
- Create Molecule tests for verification
- Document security implications

**Adding a New Control:**
1. Create `roles/system_hardening_macos/tasks/new_control.yml`
2. Define variables in `defaults/main.yml`
3. Create template if needed: `roles/system_hardening_macos/templates/config.j2`
4. Add to `tasks/main.yml`
5. Update documentation with compliance mapping
6. Add Molecule test scenario

---

## Testing Requirements

### Before Submitting PR

**All Changes Require:**
```bash
make test-fast              # Must pass: syntax + lint
make test                   # Must pass: full suite
```

**Role Changes Require:**
```bash
# For common role
cd roles/common
# Manual testing on multiple OS types
ansible-playbook ../../playbooks/provision.yml \
  -i ../../inventories/staging/hosts.yml \
  --check

# For system_hardening_macos
cd roles/system_hardening_macos
molecule test               # Full Molecule test lifecycle
```

**Documentation Changes Require:**
- Verify links work
- Ensure code examples are current
- Check formatting in rendered markdown

### Test Categories

**Syntax Tests**
```bash
ansible-playbook playbooks/provision.yml --syntax-check
```

**Lint Tests**
```bash
make lint                   # Code style and best practices
```

**Unit Tests**
```bash
make test                   # Full test suite
```

**Integration Tests**
```bash
cd roles/system_hardening_macos
molecule test               # Deploy + verify on real system
```

**Idempotence Tests**
```bash
# Run twice - second should show no changes
ansible-playbook playbooks/provision.yml \
  -i inventories/staging/hosts.yml
ansible-playbook playbooks/provision.yml \
  -i inventories/staging/hosts.yml
# Output should show: changed=0
```

---

## Security Considerations

### Reporting Security Issues

⚠️ **DO NOT** open public issues for security vulnerabilities

Instead:
1. Email: security@your-org.com with details
2. Include: Vulnerability description, impact, reproduction steps
3. Allow 48 hours for response before public disclosure
4. Reference CVSS scoring if applicable

### Security Review Checklist

All changes touching security require review by maintainers:

- [ ] No hardcoded passwords/API keys
- [ ] No privilege escalation without justification
- [ ] Follows cryptographic best practices
- [ ] Complies with relevant standards (NIST, CIS)
- [ ] Audit logging enabled if relevant
- [ ] Documentation includes security implications

---

## Style Guide

### YAML Style

```yaml
---
# Always start with --- for clarity
# Use 2 spaces for indentation (not tabs)

# Comments above items they describe
- name: Descriptive task name (min 8 chars, capital first letter)
  module_name:
    parameter: value
    multiline_param: |
      Value on multiple
      lines when needed
  become: yes
  when: condition
  tags:
    - tag1
    - tag2

# Long lists are fine, use - for readability
var_list:
  - item1
  - item2
  - item3
```

### Task Naming

```yaml
# ✅ Good: Clear, specific, present tense
- name: Install Python development headers

# ❌ Bad: Vague, past tense, too short
- name: Install stuff
- name: Installed packages
```

### Variable Naming

```yaml
# ✅ Good: Descriptive, role-prefixed
common_ssh_port: 22
macos_firewall_enabled: true

# ❌ Bad: Ambiguous, not prefixed
ssh_port: 22
firewall: true
```

### Comment Style

```yaml
# Good: Explains WHY, not WHAT (code shows what)
# SSH is restricted to key-based auth for security
common_ssh_password_authentication: "no"

# Bad: Restates code
# Set SSH password authentication to no
common_ssh_password_authentication: "no"
```

---

## Documentation Standards

### README Updates

When updating documentation:
- Keep it current with code changes
- Include examples with expected output
- Link to related documents
- Add table of contents for long docs
- Use consistent formatting

### Code Comments

```bash
# Good: Explains non-obvious logic
# Verify sshd syntax before restarting to prevent lockout
validate: '/usr/sbin/sshd -t -f %s'

# Bad: Obvious comment that just repeats code
# Check the OS family
when: ansible_os_family == "Debian"
```

### Docstrings

For complex variables or logic:
```yaml
# Role: common
# Purpose: Provides OS-agnostic server foundation configuration
#
# Configurable Areas:
# - System package updates
# - Core utility installation
# - SSH hardening
# - Kernel parameter tuning
# - Audit logging setup
```

---

## Community & Communication

### Getting Help

- **Documentation**: Check README and docs/ folder first
- **GitHub Issues**: Search closed issues for answers
- **GitHub Discussions**: Ask questions in Discussions tab
- **Community Chat**: [Link to Slack/Discord if available]

### Respectful Collaboration

We're committed to a welcoming community. Please:
- Be respectful and professional
- Assume good intent
- Provide constructive feedback
- Accept feedback gracefully
- Help others when possible

---

## FAQ

**Q: How long does PR review take?**
A: Typically 3-5 days. Urgent/security PRs prioritized.

**Q: Can I work on an issue already assigned?**
A: Comment first to check status. Most issues unassigned.

**Q: Do I need to test on real servers?**
A: For major changes yes. For docs/comments, no.

**Q: What if my PR gets rejected?**
A: That's OK! Ask what would make it mergeable or move to another issue.

**Q: How do I stay updated on project changes?**
A: Watch the repo, enable notifications, or check CHANGELOG.

**Q: Can I add dependencies?**
A: Ask first via issue. We prefer minimal dependencies.

---

## Resources

### Project Documentation
- **[README.md](README.md)** - Project overview
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design
- **[docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)** - Deployment guide
- **[docs/QUALITY_ASSURANCE.md](docs/QUALITY_ASSURANCE.md)** - Testing guide

### External Resources
- **[Ansible Documentation](https://docs.ansible.com)** - Official docs
- **[Ansible Best Practices](https://docs.ansible.com/ansible/latest/tips_tricks/ansible_tips_tricks.html)**
- **[YAML Spec](https://yaml.org/spec/)** - YAML language
- **[GitHub Flow](https://guides.github.com/introduction/flow/)** - Git workflow

### Community
- **[Ansible Community](https://github.com/ansible-community)** - Larger Ansible ecosystem
- **[Ansible Galaxy](https://galaxy.ansible.com)** - Role repository

---

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please be respectful:

- ✅ Use welcoming and inclusive language
- ✅ Be respectful of differing opinions
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the community
- ✅ Show empathy toward other community members

---

## Recognition

Contributors will be:
- Mentioned in CHANGELOG
- Listed in project contributors
- Credited in relevant documentation
- Thank you's in issue discussions

---

**Thank you for contributing to ansible-infra! 🎉**

For questions, open an issue or discussion. Happy contributing!

**Last Updated**: November 15, 2025
**Status**: Production-Ready
