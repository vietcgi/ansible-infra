.PHONY: help install lint test provision configure maintain clean

help:
	@echo "Sentinel Infrastructure - Available Commands"
	@echo "============================================="
	@echo ""
	@echo "make install              - Install Ansible collections and dependencies"
	@echo "make lint                 - Validate playbooks with ansible-lint"
	@echo "make syntax               - Check playbook syntax"
	@echo "make provision-prod       - Provision production servers"
	@echo "make provision-staging    - Provision staging servers"
	@echo "make configure-prod       - Configure production servers"
	@echo "make configure-staging    - Configure staging servers"
	@echo "make maintain-prod        - Maintenance tasks on production"
	@echo "make test-connectivity    - Test connectivity to all servers"
	@echo "make collect-facts        - Gather system facts from all servers"
	@echo "make clean                - Clean temporary files"
	@echo ""

install:
	@echo "Installing Ansible collections..."
	ansible-galaxy collection install -r requirements.yml -v
	@echo "✓ Installation complete"

lint:
	@echo "Linting playbooks..."
	@command -v ansible-lint >/dev/null 2>&1 || pip install ansible-lint
	ansible-lint playbooks/ roles/
	@echo "✓ Linting complete"

syntax:
	@echo "Checking playbook syntax..."
	ansible-playbook playbooks/provision.yml --syntax-check
	ansible-playbook playbooks/configure.yml --syntax-check
	ansible-playbook playbooks/maintenance.yml --syntax-check
	@echo "✓ Syntax check complete"

provision-prod:
	@echo "Provisioning PRODUCTION servers..."
	ansible-playbook playbooks/provision.yml -i inventories/production/hosts.yml -v

provision-staging:
	@echo "Provisioning STAGING servers..."
	ansible-playbook playbooks/provision.yml -i inventories/staging/hosts.yml -v

configure-prod:
	@echo "Configuring PRODUCTION servers..."
	ansible-playbook playbooks/configure.yml -i inventories/production/hosts.yml -v

configure-staging:
	@echo "Configuring STAGING servers..."
	ansible-playbook playbooks/configure.yml -i inventories/staging/hosts.yml -v

maintain-prod:
	@echo "Running PRODUCTION maintenance..."
	ansible-playbook playbooks/maintenance.yml -i inventories/production/hosts.yml -v

test-connectivity:
	@echo "Testing connectivity to all servers..."
	ansible all -i inventories/production/hosts.yml -m ping

collect-facts:
	@echo "Collecting facts from all servers..."
	ansible all -i inventories/production/hosts.yml -m setup -a "filter=ansible_*"

clean:
	@echo "Cleaning temporary files..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -delete
	find . -name "*.retry" -delete
	rm -rf .molecule/ .pytest_cache/
	@echo "✓ Cleanup complete"

.DEFAULT_GOAL := help
