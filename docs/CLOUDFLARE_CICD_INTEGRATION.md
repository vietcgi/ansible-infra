# Cloudflare Integration - CI/CD Integration Guide

**Date**: November 17, 2025
**Purpose**: Integrate Cloudflare automation safely into CI/CD pipelines
**Platforms**: GitHub Actions, GitLab CI, Jenkins, Azure DevOps

> **See Also**: [CLOUDFLARE_GUIDE.md](CLOUDFLARE_GUIDE.md) for comprehensive operations, troubleshooting, and backup procedures.

---

## Overview

Integrating Cloudflare automation into CI/CD enables:
- **Automated validation** before production changes
- **Drift detection** to catch unauthorized manual changes
- **Automated backups** before deployments
- **Safe deployment workflows** with approval gates
- **Comprehensive audit trails** of all changes

---

## GitHub Actions Integration

### Setup 1: Configure Repository Secrets

Store secrets in GitHub:

```
Settings → Secrets and variables → Actions

Add these secrets:
- CLOUDFLARE_API_TOKEN       (your API token)
- CLOUDFLARE_DOMAIN           (your domain)
- VAULT_PASSWORD              (Ansible vault password)
```

### Setup 2: Create GitHub Actions Workflow

Create `.github/workflows/cloudflare-deploy.yml`:

```yaml
name: Deploy Cloudflare Configuration

on:
  push:
    branches:
      - main
    paths:
      - 'roles/cloudflare_integration/**'
      - 'examples/cloudflare_*.yml'
      - '.github/workflows/cloudflare-deploy.yml'
  workflow_dispatch:  # Allow manual trigger

jobs:
  validate:
    name: Validate Configuration
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install ansible jinja2 pyyaml

      - name: Validate Ansible syntax
        run: |
          ansible-playbook --syntax-check examples/cloudflare_deployment.yml

      - name: Lint playbook
        run: |
          ansible-lint examples/cloudflare_deployment.yml || true

  drift_detection:
    name: Check for Drift
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install ansible

      - name: Run drift detection
        run: |
          ansible-playbook examples/cloudflare_drift_detection.yml \
            -e "cloudflare_api_token=${{ secrets.CLOUDFLARE_API_TOKEN }}" \
            -e "cloudflare_domain=${{ secrets.CLOUDFLARE_DOMAIN }}"

      - name: Upload drift report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: drift-reports
          path: reports/cloudflare/drift/

  dry_run:
    name: Dry-Run Deployment
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install ansible

      - name: Decrypt vault file
        env:
          VAULT_PASSWORD: ${{ secrets.VAULT_PASSWORD }}
        run: |
          echo "$VAULT_PASSWORD" > /tmp/.vault_pass
          ansible-vault decrypt inventories/production/group_vars/all/cloudflare_vault.yml \
            --vault-password-file=/tmp/.vault_pass || true

      - name: Run deployment in check mode
        run: |
          ansible-playbook examples/cloudflare_deployment.yml \
            --check \
            --ask-vault-pass \
            -e "cloudflare_api_token=${{ secrets.CLOUDFLARE_API_TOKEN }}" \
            -e "cloudflare_domain=${{ secrets.CLOUDFLARE_DOMAIN }}"

  approval:
    name: Wait for Approval
    needs: [drift_detection, dry_run]
    runs-on: ubuntu-latest
    environment:
      name: production
      reviewers:
        - '@team-leads'  # Require approval from team leads
    steps:
      - name: Request approval
        run: echo "Waiting for manual approval before production deployment..."

  deploy:
    name: Deploy to Production
    needs: approval
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install ansible

      - name: Create backup
        run: |
          ansible-playbook examples/cloudflare_backup.yml \
            -e "cloudflare_api_token=${{ secrets.CLOUDFLARE_API_TOKEN }}" \
            -e "cloudflare_domain=${{ secrets.CLOUDFLARE_DOMAIN }}"

      - name: Deploy configuration
        run: |
          ansible-playbook examples/cloudflare_deployment.yml \
            -e "cloudflare_api_token=${{ secrets.CLOUDFLARE_API_TOKEN }}" \
            -e "cloudflare_domain=${{ secrets.CLOUDFLARE_DOMAIN }}"

      - name: Validate deployment
        run: |
          ansible-playbook examples/cloudflare_idempotency_test.yml \
            -e "cloudflare_api_token=${{ secrets.CLOUDFLARE_API_TOKEN }}" \
            -e "cloudflare_domain=${{ secrets.CLOUDFLARE_DOMAIN }}"

      - name: Create deployment notification
        if: success()
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: ' Cloudflare deployment successful!\n\nDomain: ${{ secrets.CLOUDFLARE_DOMAIN }}\nBackup created\nValidation passed'
            })

      - name: Create deployment failure notification
        if: failure()
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '❌ Cloudflare deployment failed!\n\nCheck workflow logs for details'
            })

      - name: Upload backup
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: cloudflare-backup
          path: backups/cloudflare/
          retention-days: 30
```

### Setup 3: Pull Request Validation

Create `.github/workflows/cloudflare-validate-pr.yml`:

```yaml
name: Validate Cloudflare PR Changes

on:
  pull_request:
    paths:
      - 'roles/cloudflare_integration/**'
      - 'examples/cloudflare_*.yml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install ansible-lint ansible

      - name: Lint changes
        run: |
          ansible-lint examples/cloudflare_deployment.yml

      - name: Check for syntax errors
        run: |
          ansible-playbook --syntax-check examples/cloudflare_deployment.yml

      - name: Comment on PR
        if: success()
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: ' Cloudflare configuration validation passed\n\n- Syntax check: OK\n- Linting: OK\n- Ready for dry-run'
            })
```

---

## GitLab CI Integration

Create `.gitlab-ci.yml` (in repository root):

```yaml
stages:
  - validate
  - check_drift
  - dry_run
  - approval
  - deploy

variables:
  ANSIBLE_HOST_KEY_CHECKING: "false"

validate_syntax:
  stage: validate
  image: python:3.11
  before_script:
    - pip install ansible
  script:
    - ansible-playbook --syntax-check examples/cloudflare_deployment.yml
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

drift_detection:
  stage: check_drift
  image: python:3.11
  before_script:
    - pip install ansible
    - mkdir -p reports/cloudflare/drift
  script:
    - ansible-playbook examples/cloudflare_drift_detection.yml
      -e "cloudflare_api_token=$CLOUDFLARE_API_TOKEN"
      -e "cloudflare_domain=$CLOUDFLARE_DOMAIN"
  artifacts:
    paths:
      - reports/cloudflare/drift/
    expire_in: 30 days
  allow_failure: true
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

dry_run:
  stage: dry_run
  image: python:3.11
  before_script:
    - pip install ansible
  script:
    - ansible-playbook examples/cloudflare_deployment.yml
      --check
      -e "cloudflare_api_token=$CLOUDFLARE_API_TOKEN"
      -e "cloudflare_domain=$CLOUDFLARE_DOMAIN"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

approval:
  stage: approval
  script:
    - echo "Awaiting manual approval..."
  when: manual
  only:
    - main

backup:
  stage: deploy
  image: python:3.11
  before_script:
    - pip install ansible
  script:
    - ansible-playbook examples/cloudflare_backup.yml
      -e "cloudflare_api_token=$CLOUDFLARE_API_TOKEN"
      -e "cloudflare_domain=$CLOUDFLARE_DOMAIN"
  artifacts:
    paths:
      - backups/cloudflare/
    expire_in: 90 days
  when: manual
  only:
    - main

deploy:
  stage: deploy
  image: python:3.11
  before_script:
    - pip install ansible
  script:
    - echo "Deploying Cloudflare configuration..."
    - ansible-playbook examples/cloudflare_deployment.yml
      -e "cloudflare_api_token=$CLOUDFLARE_API_TOKEN"
      -e "cloudflare_domain=$CLOUDFLARE_DOMAIN"
    - ansible-playbook examples/cloudflare_idempotency_test.yml
      -e "cloudflare_api_token=$CLOUDFLARE_API_TOKEN"
      -e "cloudflare_domain=$CLOUDFLARE_DOMAIN"
  when: manual
  only:
    - main
```

---

## Jenkins Pipeline Integration

Create `Jenkinsfile` in repository root:

```groovy
pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['VALIDATE', 'DRY_RUN', 'DEPLOY'],
            description: 'What to execute'
        )
    }

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        stage('Validate') {
            steps {
                script {
                    echo "✓ Validating Cloudflare configuration..."
                    sh '''
                        python -m pip install ansible
                        ansible-playbook --syntax-check examples/cloudflare_deployment.yml
                    '''
                }
            }
        }

        stage('Drift Detection') {
            steps {
                script {
                    echo "✓ Checking for configuration drift..."
                    withCredentials([string(credentialsId: 'cloudflare_api_token', variable: 'TOKEN')]) {
                        sh '''
                            ansible-playbook examples/cloudflare_drift_detection.yml \
                              -e "cloudflare_api_token=${TOKEN}" \
                              -e "cloudflare_domain=${CLOUDFLARE_DOMAIN}"
                        '''
                    }
                }
            }
        }

        stage('Dry-Run') {
            when {
                expression { params.ENVIRONMENT == 'DRY_RUN' || params.ENVIRONMENT == 'DEPLOY' }
            }
            steps {
                script {
                    echo "✓ Running deployment in check mode..."
                    withCredentials([string(credentialsId: 'cloudflare_api_token', variable: 'TOKEN')]) {
                        sh '''
                            ansible-playbook examples/cloudflare_deployment.yml \
                              --check \
                              -e "cloudflare_api_token=${TOKEN}" \
                              -e "cloudflare_domain=${CLOUDFLARE_DOMAIN}"
                        '''
                    }
                }
            }
        }

        stage('Approval') {
            when {
                expression { params.ENVIRONMENT == 'DEPLOY' }
            }
            steps {
                input message: 'Deploy to production?', ok: 'Deploy'
            }
        }

        stage('Backup') {
            when {
                expression { params.ENVIRONMENT == 'DEPLOY' }
            }
            steps {
                script {
                    echo "✓ Creating backup..."
                    withCredentials([string(credentialsId: 'cloudflare_api_token', variable: 'TOKEN')]) {
                        sh '''
                            ansible-playbook examples/cloudflare_backup.yml \
                              -e "cloudflare_api_token=${TOKEN}" \
                              -e "cloudflare_domain=${CLOUDFLARE_DOMAIN}"
                        '''
                    }
                    archiveArtifacts artifacts: 'backups/cloudflare/**', allowEmptyArchive: true
                }
            }
        }

        stage('Deploy') {
            when {
                expression { params.ENVIRONMENT == 'DEPLOY' }
            }
            steps {
                script {
                    echo "✓ Deploying Cloudflare configuration..."
                    withCredentials([string(credentialsId: 'cloudflare_api_token', variable: 'TOKEN')]) {
                        sh '''
                            ansible-playbook examples/cloudflare_deployment.yml \
                              -e "cloudflare_api_token=${TOKEN}" \
                              -e "cloudflare_domain=${CLOUDFLARE_DOMAIN}"
                        '''
                    }
                }
            }
        }

        stage('Validate Deployment') {
            when {
                expression { params.ENVIRONMENT == 'DEPLOY' }
            }
            steps {
                script {
                    echo "✓ Validating deployment..."
                    withCredentials([string(credentialsId: 'cloudflare_api_token', variable: 'TOKEN')]) {
                        sh '''
                            ansible-playbook examples/cloudflare_idempotency_test.yml \
                              -e "cloudflare_api_token=${TOKEN}" \
                              -e "cloudflare_domain=${CLOUDFLARE_DOMAIN}"
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo " Pipeline completed successfully"
        }
        failure {
            echo "❌ Pipeline failed - check logs"
        }
    }
}
```

---

## Best Practices for CI/CD

### 1. Approval Gates

Always require manual approval before production deployment:

```yaml
# GitHub Actions
environment:
  name: production
  reviewers:
    - '@team-leads'
```

### 2. Drift Detection

Run drift detection before deployment to catch unauthorized changes:

```bash
ansible-playbook examples/cloudflare_drift_detection.yml
```

### 3. Automated Backups

Always create a backup before deploying:

```bash
ansible-playbook examples/cloudflare_backup.yml
```

### 4. Dry-Run First

Run in check mode to show what will change:

```bash
ansible-playbook examples/cloudflare_deployment.yml --check
```

### 5. Post-Deployment Validation

Verify the deployment was successful:

```bash
ansible-playbook examples/cloudflare_idempotency_test.yml
```

### 6. Notifications

Send notifications on success/failure:

```yaml
# GitHub Actions
- uses: actions/github-script@v6
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: ' Deployment successful!'
      })
```

---

## Security Considerations

### 1. Store Secrets Securely

**Never commit secrets to git:**

```yaml
# ❌ WRONG
cloudflare_api_token: "abc123def456"

#  RIGHT
cloudflare_api_token: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### 2. Limit Access

```yaml
# GitHub Actions - Require approval from specific team
environment:
  name: production
  reviewers:
    - '@security-team'
    - '@devops-team'
```

### 3. Audit Trail

All deployments appear in:
- GitHub Actions logs
- GitLab CI logs
- Jenkins build history
- Git commit history

### 4. Restrict Who Can Deploy

```yaml
# GitHub Actions - Only main branch
rules:
  - if: '$CI_COMMIT_BRANCH == "main"'
```

---

## Troubleshooting

### Issue: "Authentication failed"

**Check**:
1. API token is correct in secrets
2. Token hasn't expired
3. Token has necessary permissions

**Fix**:
```bash
# Test authentication manually
curl -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/user
```

### Issue: "Zone not found"

**Check**:
1. Domain name is correct
2. Domain is added to Cloudflare account

**Fix**:
```bash
# Verify domain
curl -H "Authorization: Bearer TOKEN" \
  https://api.cloudflare.com/client/v4/zones?name=example.com
```

### Issue: "Deployment fails with permission denied"

**Check**:
1. API token has Zone:Edit scopes
2. Token has WAF:Edit if WAF is being configured
3. Token has Settings:Edit for SSL/TLS changes

---

## Example CI/CD Workflows

### Basic: On Commit to Main

```yaml
# Deploy automatically when code is pushed to main
on:
  push:
    branches: [main]
    paths: [roles/cloudflare_integration/**]
```

### Advanced: Pull Request with Approvals

```yaml
# Validate on PR, deploy only with approval on main
on:
  pull_request:
  push:
    branches: [main]
```

### Conservative: Manual Trigger Only

```yaml
# Never deploy automatically, always require manual trigger
on:
  workflow_dispatch
```

---

**Last Updated**: November 17, 2025
**Status**: Production-Ready
