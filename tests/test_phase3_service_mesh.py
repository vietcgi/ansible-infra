"""
Tests for PHASE 3 Service Mesh Integration

This module validates the service mesh integration wrapper with Istio/Linkerd
configuration, traffic management, mTLS, and distributed tracing capabilities.
"""

import os
import yaml
from pathlib import Path


def test_service_mesh_wrapper_file_exists():
    """Verify service mesh integration wrapper task file exists."""
    wrapper_file = "roles/common/tasks/service_mesh_integration_wrapper.yml"
    assert Path(wrapper_file).exists(), f"Missing service mesh wrapper: {wrapper_file}"


def test_service_mesh_wrapper_yaml_valid():
    """Verify service mesh wrapper YAML is valid."""
    wrapper_file = "roles/common/tasks/service_mesh_integration_wrapper.yml"
    with open(wrapper_file, "r") as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in {wrapper_file}: {e}")


def test_service_mesh_wrapper_fqcn_compliance():
    """Verify service mesh wrapper uses FQCN for all modules."""
    wrapper_file = "roles/common/tasks/service_mesh_integration_wrapper.yml"
    with open(wrapper_file, "r") as f:
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

    # These patterns should use FQCN or not appear at all
    for pattern in forbidden_patterns:
        # Allow some patterns if they're using FQCN
        if pattern in content:
            # Check if they're using FQCN
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if pattern in line:
                    # Should use ansible.builtin, kubernetes.core, or community prefix
                    if not any(fqcn in lines[max(0, i-2):i+3] for fqcn in
                              ['ansible.builtin', 'kubernetes.core', 'community']):
                        assert False, f"Found non-FQCN module usage: {pattern}"


def test_service_mesh_wrapper_contains_required_blocks():
    """Verify service mesh wrapper contains all required functionality blocks."""
    wrapper_file = "roles/common/tasks/service_mesh_integration_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    required_sections = [
        "Validate service mesh prerequisites",
        "Create monitoring namespace",
        "Install Istio operator",
        "Install Linkerd service mesh",
        "Configure Istio ingress gateway",
        "Enable sidecar auto-injection",
        "Create Istio VirtualService",
        "Create Istio DestinationRule",
        "Create PeerAuthentication for mTLS",
        "Create AuthorizationPolicy",
        "Configure Istio telemetry for tracing",
        "Install Kiali",
        "Install Jaeger distributed tracing",
        "Verify service mesh pods status",
    ]

    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_service_mesh_defaults_variables_exist():
    """Verify defaults/main.yml includes service mesh variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for service mesh core variables
    service_mesh_vars = [
        "service_mesh_enabled",
        "service_mesh_type",
        "service_mesh_istio_version",
        "service_mesh_sidecar_injection_enabled",
        "service_mesh_traffic_management_enabled",
        "service_mesh_mtls_enabled",
        "service_mesh_mtls_mode",
        "service_mesh_authorization_enabled",
        "service_mesh_tracing_enabled",
        "service_mesh_visualization_enabled",
    ]

    for var in service_mesh_vars:
        assert var in defaults, f"Missing service mesh variable: {var}"


def test_service_mesh_variables_have_defaults():
    """Verify all service mesh variables have sensible default values."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check service mesh type is valid
    mesh_type = defaults.get("service_mesh_type")
    assert mesh_type in ["istio", "linkerd"], f"Invalid service mesh type: {mesh_type}"

    # Check mTLS mode is valid
    mtls_mode = defaults.get("service_mesh_mtls_mode")
    assert mtls_mode in ["PERMISSIVE", "STRICT"], f"Invalid mTLS mode: {mtls_mode}"

    # Check Istio version is set
    istio_version = defaults.get("service_mesh_istio_version")
    assert istio_version and isinstance(istio_version, str), "Istio version not properly set"

    # Check proxy resources are reasonable
    proxy_cpu = defaults.get("service_mesh_proxy_cpu")
    assert "m" in proxy_cpu or "Mi" in proxy_cpu, f"Invalid proxy CPU: {proxy_cpu}"

    proxy_memory = defaults.get("service_mesh_proxy_memory")
    assert "Mi" in proxy_memory or "Gi" in proxy_memory, f"Invalid proxy memory: {proxy_memory}"


def test_service_mesh_traffic_management_variables():
    """Verify traffic management variables are properly configured."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check timeout format
    request_timeout = defaults.get("service_mesh_request_timeout")
    assert "s" in request_timeout, "Request timeout should be in seconds format"

    # Check load balancing algorithm
    lb_algo = defaults.get("service_mesh_load_balancing_algorithm")
    valid_algos = ["ROUND_ROBIN", "LEAST_REQUEST", "RANDOM", "PASSTHROUGH"]
    assert lb_algo in valid_algos, f"Invalid load balancing algorithm: {lb_algo}"

    # Check connection limits are positive
    max_conn = defaults.get("service_mesh_max_connections")
    assert max_conn > 0, "Max connections should be positive"


def test_service_mesh_security_variables():
    """Verify security-related service mesh variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check mTLS is properly configured
    mtls_enabled = defaults.get("service_mesh_mtls_enabled")
    assert isinstance(mtls_enabled, bool), "mTLS enabled should be boolean"

    # Check authorization is configured
    authz_enabled = defaults.get("service_mesh_authorization_enabled")
    assert isinstance(authz_enabled, bool), "Authorization enabled should be boolean"

    # Check JWT settings if enabled
    jwt_enabled = defaults.get("service_mesh_jwt_enabled")
    if jwt_enabled:
        jwt_issuer = defaults.get("service_mesh_jwt_issuer")
        assert jwt_issuer, "JWT issuer must be set if JWT is enabled"


def test_service_mesh_observability_variables():
    """Verify observability-related variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check tracing is configured
    tracing_enabled = defaults.get("service_mesh_tracing_enabled")
    assert isinstance(tracing_enabled, bool), "Tracing enabled should be boolean"

    # Check visualization is configured
    viz_enabled = defaults.get("service_mesh_visualization_enabled")
    assert isinstance(viz_enabled, bool), "Visualization enabled should be boolean"

    # Check trace sampling is valid (0-100 or percentage format)
    trace_sampling = defaults.get("service_mesh_trace_sampling")
    assert 0 <= trace_sampling <= 100, f"Trace sampling should be 0-100: {trace_sampling}"


def test_service_mesh_wrapper_line_count():
    """Verify service mesh wrapper meets minimum LOC requirement."""
    wrapper_file = "roles/common/tasks/service_mesh_integration_wrapper.yml"
    with open(wrapper_file, "r") as f:
        loc = len(f.readlines())

    # Service mesh wrapper should be substantial (400-800 LOC)
    assert loc >= 300, f"Service mesh wrapper too small: {loc} LOC (minimum 300)"
    assert loc <= 1000, f"Service mesh wrapper too large: {loc} LOC (maximum 1000)"


def test_service_mesh_wrapper_in_tasks_main():
    """Verify service mesh wrapper is imported in tasks/main.yml."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    assert "service_mesh_integration_wrapper.yml" in content, \
        "Missing service mesh wrapper import in tasks/main.yml"


def test_service_mesh_integration_ordering():
    """Verify service mesh wrapper is imported after orchestration foundations."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    k8s_pos = content.find("kubernetes_orchestration_wrapper.yml")
    app_pos = content.find("application_deployment_wrapper.yml")
    mesh_pos = content.find("service_mesh_integration_wrapper.yml")

    assert k8s_pos != -1, "Kubernetes wrapper not found"
    assert app_pos != -1, "Application wrapper not found"
    assert mesh_pos != -1, "Service mesh wrapper not found"

    # Service mesh should be after both Kubernetes and application wrappers
    assert k8s_pos < mesh_pos, "Service mesh should be imported after Kubernetes"
    assert app_pos < mesh_pos, "Service mesh should be imported after application deployment"


def test_service_mesh_variables_count():
    """Verify sufficient service mesh variables are defined."""
    with open("roles/common/defaults/main.yml", "r") as f:
        content = f.read()

    # Count service_mesh_ prefixed variables
    mesh_var_count = content.count("service_mesh_")

    # Should have at least 30 service mesh variables
    assert mesh_var_count >= 30, f"Too few service mesh variables: {mesh_var_count}"


def test_service_mesh_feature_completeness():
    """Verify service mesh implementation covers key features."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    required_features = [
        "traffic management",
        "mtls",
        "sidecar",
        "distributed tracing",
        "visualization",
        "ingress gateway",
        "authorization",
    ]

    for feature in required_features:
        assert feature.lower() in content.lower(), f"Missing feature: {feature}"


def test_service_mesh_istio_linkerd_support():
    """Verify both Istio and Linkerd support is implemented."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    # Check for Istio installation
    assert "Install Istio operator" in content or "istio" in content.lower(), \
        "Missing Istio support"

    # Check for Linkerd installation
    assert "Install Linkerd service mesh" in content or "linkerd" in content.lower(), \
        "Missing Linkerd support"


def test_service_mesh_helm_integration():
    """Verify Helm is used for service mesh deployment."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    # Service mesh should use Helm for installation
    assert "helm" in content.lower(), "Service mesh should use Helm for deployment"


def test_service_mesh_kubernetes_api_usage():
    """Verify service mesh uses Kubernetes API correctly."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    # Should use kubernetes.core module
    assert "kubernetes.core.k8s" in content, \
        "Service mesh should use kubernetes.core.k8s module"


def test_service_mesh_error_handling():
    """Verify service mesh wrapper has proper error handling."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    # Check for block/rescue structure
    assert "block:" in content, "Service mesh wrapper should have block structure"
    assert "rescue:" in content, "Service mesh wrapper should have rescue block"


def test_service_mesh_idempotency():
    """Verify service mesh wrapper supports idempotent operations."""
    with open("roles/common/tasks/service_mesh_integration_wrapper.yml", "r") as f:
        content = f.read()

    # Check for idempotent patterns
    idempotent_patterns = [
        "state: present",
        "helm upgrade",
        "ignore_errors",
    ]

    for pattern in idempotent_patterns:
        assert pattern in content, f"Missing idempotent pattern: {pattern}"
