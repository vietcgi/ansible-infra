# pfSense WireGuard Test Environment
#
# Prerequisites:
#   - VirtualBox installed
#   - Vagrant installed
#   - pfSense CE ISO downloaded

PFSENSE_ISO ?= ~/Downloads/pfSense-CE-2.7.2-RELEASE-amd64.iso
PFSENSE_VM_NAME = pfsense-test
VBOX_HOSTONLY_NET = vboxnet0

.PHONY: help setup-network create-vm install start stop destroy test ansible-test

help:
	@echo "pfSense WireGuard Test Environment"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup-network    - Create VirtualBox host-only network"
	@echo "  2. make create-vm        - Create pfSense VM (then install manually)"
	@echo "  3. make start            - Start the test environment"
	@echo "  4. make ansible-test     - Run Ansible playbook against test VM"
	@echo ""
	@echo "Targets:"
	@echo "  setup-network  - Create VirtualBox host-only network (192.168.56.0/24)"
	@echo "  create-vm      - Create pfSense VM from ISO"
	@echo "  start          - Start pfSense and client VMs"
	@echo "  stop           - Stop all VMs"
	@echo "  destroy        - Destroy all VMs"
	@echo "  ssh-pfsense    - SSH to pfSense"
	@echo "  ssh-client     - SSH to test client"
	@echo "  test           - Run connectivity tests"
	@echo "  ansible-test   - Run Ansible playbook"

setup-network:
	@echo "Setting up VirtualBox host-only network..."
	VBoxManage hostonlyif create 2>/dev/null || true
	VBoxManage hostonlyif ipconfig $(VBOX_HOSTONLY_NET) --ip 192.168.56.1 --netmask 255.255.255.0
	@echo "Host-only network configured: 192.168.56.0/24"

create-vm:
	@echo "Creating pfSense VM..."
	@if [ ! -f "$(PFSENSE_ISO)" ]; then \
		echo "ERROR: pfSense ISO not found at $(PFSENSE_ISO)"; \
		echo "Download from: https://www.pfsense.org/download/"; \
		exit 1; \
	fi
	VBoxManage createvm --name $(PFSENSE_VM_NAME) --ostype FreeBSD_64 --register
	VBoxManage modifyvm $(PFSENSE_VM_NAME) --memory 1024 --cpus 1 --vram 16
	VBoxManage modifyvm $(PFSENSE_VM_NAME) --nic1 nat --nic2 hostonly --hostonlyadapter2 $(VBOX_HOSTONLY_NET)
	VBoxManage createhd --filename ~/VirtualBox\ VMs/$(PFSENSE_VM_NAME)/$(PFSENSE_VM_NAME).vdi --size 8192
	VBoxManage storagectl $(PFSENSE_VM_NAME) --name "SATA Controller" --add sata
	VBoxManage storageattach $(PFSENSE_VM_NAME) --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium ~/VirtualBox\ VMs/$(PFSENSE_VM_NAME)/$(PFSENSE_VM_NAME).vdi
	VBoxManage storagectl $(PFSENSE_VM_NAME) --name "IDE Controller" --add ide
	VBoxManage storageattach $(PFSENSE_VM_NAME) --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium "$(PFSENSE_ISO)"
	VBoxManage modifyvm $(PFSENSE_VM_NAME) --boot1 dvd --boot2 disk
	@echo ""
	@echo "VM created. Now:"
	@echo "  1. VBoxManage startvm $(PFSENSE_VM_NAME)"
	@echo "  2. Complete pfSense installation"
	@echo "  3. Configure WAN (em0) as DHCP, LAN (em1) as 192.168.56.10/24"
	@echo "  4. Enable SSH in System > Advanced > Admin Access"
	@echo "  5. After install, eject ISO and reboot"

start:
	@echo "Starting test environment..."
	VBoxManage startvm $(PFSENSE_VM_NAME) --type headless 2>/dev/null || true
	vagrant up client
	@echo "Environment started. pfSense at 192.168.56.10"

stop:
	@echo "Stopping test environment..."
	VBoxManage controlvm $(PFSENSE_VM_NAME) poweroff 2>/dev/null || true
	vagrant halt client

destroy:
	@echo "Destroying test environment..."
	VBoxManage controlvm $(PFSENSE_VM_NAME) poweroff 2>/dev/null || true
	VBoxManage unregistervm $(PFSENSE_VM_NAME) --delete 2>/dev/null || true
	vagrant destroy -f client

ssh-pfsense:
	ssh -o StrictHostKeyChecking=no admin@192.168.56.10

ssh-client:
	vagrant ssh client

test:
	@echo "Testing connectivity..."
	@echo "--- pfSense SSH ---"
	ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 admin@192.168.56.10 "uname -a" || echo "SSH failed"
	@echo ""
	@echo "--- Client Gateway ---"
	vagrant ssh client -c "ip route | grep default"
	@echo ""
	@echo "--- Client Internet (through pfSense) ---"
	vagrant ssh client -c "curl -s https://api.ipify.org" || echo "No internet"

ansible-test:
	@echo "Running Ansible playbook against test pfSense..."
	cd ../.. && ansible-playbook playbooks/pfsense-wireguard.yml \
		-i inventories/pfsense/hosts.yml \
		-l pfsense-test \
		-e "ansible_host=192.168.56.10" \
		-e "ansible_user=admin" \
		-v

ansible-check:
	@echo "Dry-run Ansible playbook..."
	cd ../.. && ansible-playbook playbooks/pfsense-wireguard.yml \
		-i inventories/pfsense/hosts.yml \
		-l pfsense-test \
		-e "ansible_host=192.168.56.10" \
		-e "ansible_user=admin" \
		--check -v
