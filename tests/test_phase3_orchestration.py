"""
Tests for PHASE 3 Final Integration & Orchestration

This module validates the PHASE 3 implementation with Kubernetes orchestration,
application deployment automation, and advanced monitoring.
Tests ensure proper integration of cluster orchestration and application lifecycle.
"""

import os
import yaml
from pathlib import Path


def test_phase3_wrapper_tasks_exist():
    """Verify all PHASE 3 wrapper task files exist."""
    task_files = [
        "roles/common/tasks/kubernetes_orchestration_wrapper.yml",
        "roles/common/tasks/application_deployment_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase3_task_files_valid_yaml():
    """Verify all PHASE 3 task files are valid YAML."""
    task_files = [
        "roles/common/tasks/kubernetes_orchestration_wrapper.yml",
        "roles/common/tasks/application_deployment_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_defaults_main_yml_contains_kubernetes_variables():
    """Verify defaults/main.yml includes PHASE 3 Kubernetes variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Kubernetes variables
    kubernetes_vars = [
        "orchestration_kubernetes_enabled",
        "orchestration_kubernetes_version",
        "orchestration_cluster_name",
        "orchestration_kubernetes_pod_network",
        "orchestration_kubernetes_service_network",
        "orchestration_container_runtime",
        "orchestration_kubernetes_network_plugin",
    ]

    for var in kubernetes_vars:
        assert var in defaults, f"Missing Kubernetes variable: {var}"


def test_defaults_main_yml_contains_deployment_variables():
    """Verify defaults/main.yml includes PHASE 3 deployment variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key deployment variables
    deployment_vars = [
        "deployment_automation_enabled",
        "deployment_namespace",
        "deployment_strategy",
        "deployment_environment",
        "deployment_autoscaling_enabled",
    ]

    for var in deployment_vars:
        assert var in defaults, f"Missing deployment variable: {var}"


def test_kubernetes_orchestration_wrapper_contains_fqcn():
    """Verify kubernetes_orchestration_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/kubernetes_orchestration_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - file:",
        "  - copy:",
        "  - apt:",
        "  - yum:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in kubernetes_orchestration_wrapper: {pattern}"


def test_application_deployment_wrapper_contains_fqcn():
    """Verify application_deployment_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/application_deployment_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - file:",
        "  - copy:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in application_deployment_wrapper: {pattern}"


def test_phase3_line_count_validation():
    """Verify PHASE 3 implementation is within expected LOC range."""
    task_files = [
        "roles/common/tasks/kubernetes_orchestration_wrapper.yml",
        "roles/common/tasks/application_deployment_wrapper.yml",
    ]

    total_loc = 0
    for task_file in task_files:
        with open(task_file, "r") as f:
            total_loc += len(f.readlines())

    # Expected range: 600-1200 LOC for PHASE 3 wrapper tasks
    assert total_loc >= 600, f"PHASE 3 wrapper tasks too small: {total_loc} LOC"
    assert total_loc <= 1200, f"PHASE 3 wrapper tasks too large: {total_loc} LOC"


def test_phase3_tasks_main_yml_has_imports():
    """Verify tasks/main.yml includes PHASE 3 task imports."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    required_imports = [
        "kubernetes_orchestration_wrapper.yml",
        "application_deployment_wrapper.yml",
    ]

    for import_file in required_imports:
        assert import_file in content, f"Missing import in tasks/main.yml: {import_file}"


def test_defaults_main_yml_contains_monitoring_variables():
    """Verify defaults/main.yml includes PHASE 3 monitoring integration variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for monitoring variables
    monitoring_vars = [
        "deployment_monitoring_enabled",
    ]

    for var in monitoring_vars:
        assert var in defaults, f"Missing monitoring variable: {var}"


def test_kubernetes_variables_have_sensible_defaults():
    """Verify PHASE 3 Kubernetes variables have sensible default values."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check default kubernetes version is valid
    k8s_version = defaults.get("orchestration_kubernetes_version")
    assert k8s_version is not None, "Kubernetes version not set"
    assert isinstance(k8s_version, str), "Kubernetes version should be a string"

    # Check pod network CIDR is valid
    pod_network = defaults.get("orchestration_kubernetes_pod_network", "10.244.0.0/16")
    assert "/" in pod_network, "Pod network CIDR should include netmask"

    # Check service network CIDR is valid
    service_network = defaults.get("orchestration_kubernetes_service_network", "10.96.0.0/12")
    assert "/" in service_network, "Service network CIDR should include netmask"


def test_deployment_variables_have_sensible_defaults():
    """Verify PHASE 3 deployment variables have sensible default values."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check default namespace is set
    assert defaults.get("deployment_namespace"), "Deployment namespace not set"

    # Check deployment strategy is valid
    strategy = defaults.get("deployment_strategy", "rolling")
    assert strategy in ["rolling", "canary", "blue-green"], f"Invalid deployment strategy: {strategy}"

    # Check environment is set
    assert defaults.get("deployment_environment"), "Deployment environment not set"


def test_kubernetes_wrapper_contains_required_sections():
    """Verify kubernetes_orchestration_wrapper.yml contains all required sections."""
    with open("roles/common/tasks/kubernetes_orchestration_wrapper.yml", "r") as f:
        content = f.read()

    required_sections = [
        "Validate Kubernetes prerequisites",
        "Install container runtime",
        "Disable swap",
        "Configure kernel parameters",
        "Install Kubernetes components",
        "Initialize Kubernetes cluster",
        "Install network plugin",
        "Verify cluster health",
    ]

    for section in required_sections:
        assert section in content, f"Missing section in kubernetes wrapper: {section}"


def test_application_deployment_wrapper_contains_required_sections():
    """Verify application_deployment_wrapper.yml contains all required sections."""
    with open("roles/common/tasks/application_deployment_wrapper.yml", "r") as f:
        content = f.read()

    required_sections = [
        "Create deployment namespace",
        "Deploy applications",
        "Create Kubernetes Services",
        "Horizontal Pod Autoscaler",
        "Network Policies",
        "Verify deployment status",
    ]

    for section in required_sections:
        assert section in content, f"Missing section in application deployment wrapper: {section}"


def test_phase3_implementation_completeness():
    """Verify PHASE 3 implementation includes orchestration and deployment automation."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Ensure orchestration is configured
    assert "orchestration_kubernetes_enabled" in defaults, "Kubernetes orchestration not configured"
    assert "deployment_automation_enabled" in defaults, "Application deployment automation not configured"

    # Ensure deployment strategies are available
    assert "deployment_strategy" in defaults, "Deployment strategy not configured"
    assert "deployment_autoscaling_enabled" in defaults, "Autoscaling not configured"


def test_phase3_security_variables():
    """Verify PHASE 3 includes security-related variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for security-related variables
    security_vars = [
        "deployment_network_policies_enabled",
    ]

    for var in security_vars:
        assert var in defaults, f"Missing security variable: {var}"


def test_phase3_monitoring_integration():
    """Verify PHASE 3 includes monitoring integration variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check monitoring integration
    assert "deployment_monitoring_enabled" in defaults, "Monitoring integration not configured"


def test_phase3_total_line_count():
    """Verify PHASE 3 implementation meets minimum LOC requirement."""
    task_files = [
        "roles/common/tasks/kubernetes_orchestration_wrapper.yml",
        "roles/common/tasks/application_deployment_wrapper.yml",
    ]

    total_loc = sum(len(open(f).readlines()) for f in task_files)
    assert total_loc >= 600, f"PHASE 3 implementation too small: {total_loc} LOC (minimum 600)"


def test_phase3_production_readiness():
    """Verify PHASE 3 implementation includes production-ready features."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for high availability features
    assert "deployment_autoscaling_enabled" in defaults, "Auto-scaling not configured for HA"

    # Check for monitoring
    assert "deployment_monitoring_enabled" in defaults, "Monitoring not configured"

    # Check for security
    assert "deployment_network_policies_enabled" in defaults, "Network policies not configured"


def test_kubernetes_and_deployment_integration():
    """Verify Kubernetes and deployment wrappers are properly integrated."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    # Both should be imported in order
    k8s_pos = content.find("kubernetes_orchestration_wrapper.yml")
    deploy_pos = content.find("application_deployment_wrapper.yml")

    assert k8s_pos != -1, "Kubernetes wrapper not imported"
    assert deploy_pos != -1, "Application deployment wrapper not imported"
    assert k8s_pos < deploy_pos, "Kubernetes should be imported before application deployment"
