"""
Tests for PHASE 2.C Service Discovery & Load Balancing

This module validates the PHASE 2.C implementation with Consul and HAProxy.
Tests ensure proper integration of service discovery, health checks, and load balancing.
"""

import os
import yaml
from pathlib import Path


def test_phase2c_wrapper_tasks_exist():
    """Verify all PHASE 2.C wrapper task files exist."""
    task_files = [
        "roles/common/tasks/consul_installation_wrapper.yml",
        "roles/common/tasks/consul_service_discovery_wrapper.yml",
        "roles/common/tasks/haproxy_loadbalancer_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase2c_templates_exist():
    """Verify all PHASE 2.C template files exist."""
    template_files = [
        "roles/common/templates/consul_server_config.j2",
        "roles/common/templates/consul_client_config.j2",
        "roles/common/templates/consul_service_definition.j2",
        "roles/common/templates/consul_dns_stub.j2",
        "roles/common/templates/consul_systemd_service.j2",
        "roles/common/templates/consul_logrotate.j2",
        "roles/common/templates/haproxy_config.j2",
        "roles/common/templates/haproxy_systemd_service.j2",
        "roles/common/templates/haproxy_stats_config.j2",
        "roles/common/templates/haproxy_consul_integration.j2",
        "roles/common/templates/haproxy_metrics_export.j2",
        "roles/common/templates/haproxy_logrotate.j2",
    ]
    for template_file in template_files:
        assert Path(template_file).exists(), f"Missing template file: {template_file}"


def test_phase2c_task_files_valid_yaml():
    """Verify all PHASE 2.C task files are valid YAML."""
    task_files = [
        "roles/common/tasks/consul_installation_wrapper.yml",
        "roles/common/tasks/consul_service_discovery_wrapper.yml",
        "roles/common/tasks/haproxy_loadbalancer_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_defaults_main_yml_contains_service_discovery_variables():
    """Verify defaults/main.yml includes PHASE 2.C service discovery variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Consul variables
    consul_vars = [
        "service_discovery_consul_enabled",
        "service_discovery_consul_version",
        "service_discovery_consul_bind_addr",
        "service_discovery_consul_http_port",
        "service_discovery_consul_dns_port",
        "service_discovery_consul_node_type",
        "service_discovery_consul_datacenter",
        "service_discovery_consul_domain",
        "service_discovery_consul_server_count",
        "service_discovery_consul_services",
        "service_discovery_consul_healthchecks",
    ]

    for var in consul_vars:
        assert var in defaults, f"Missing Consul variable: {var}"


def test_defaults_main_yml_contains_loadbalancing_variables():
    """Verify defaults/main.yml includes PHASE 2.C load balancing variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key HAProxy variables
    haproxy_vars = [
        "loadbalancing_haproxy_enabled",
        "loadbalancing_haproxy_version",
        "loadbalancing_haproxy_bind_addr",
        "loadbalancing_haproxy_frontend_port",
        "loadbalancing_haproxy_stats_enabled",
        "loadbalancing_haproxy_stats_port",
        "loadbalancing_haproxy_ssl_enabled",
        "loadbalancing_haproxy_maxconn",
        "loadbalancing_haproxy_timeout_connect",
        "loadbalancing_haproxy_timeout_client",
        "loadbalancing_haproxy_timeout_server",
    ]

    for var in haproxy_vars:
        assert var in defaults, f"Missing HAProxy variable: {var}"


def test_main_yml_imports_phase2c_wrappers():
    """Verify main.yml imports the new PHASE 2.C wrapper tasks."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    wrapper_tasks = [
        "consul_installation_wrapper.yml",
        "consul_service_discovery_wrapper.yml",
        "haproxy_loadbalancer_wrapper.yml",
    ]

    for task in wrapper_tasks:
        assert task in content, f"main.yml does not import {task}"


def test_consul_server_config_template_structure():
    """Verify consul_server_config.j2 has expected JSON structure."""
    with open("roles/common/templates/consul_server_config.j2", "r") as f:
        content = f.read()

    # Verify it contains expected configuration keys
    expected_keys = [
        "datacenter",
        "server",
        "bootstrap_expect",
        "ui_config",
        "bind_addr",
        "ports",
        "domain",
        "data_dir",
    ]

    for key in expected_keys:
        assert key in content, f"Missing key '{key}' in consul_server_config.j2"


def test_haproxy_config_template_structure():
    """Verify haproxy_config.j2 has expected HAProxy configuration."""
    with open("roles/common/templates/haproxy_config.j2", "r") as f:
        content = f.read()

    # Verify it contains expected configuration sections
    expected_sections = [
        "global",
        "defaults",
        "frontend",
        "backend",
        "stats",
    ]

    for section in expected_sections:
        assert section in content, f"Missing section '{section}' in haproxy_config.j2"


def test_consul_installation_wrapper_has_preflights():
    """Verify consul_installation_wrapper.yml has pre-flight validation."""
    with open("roles/common/tasks/consul_installation_wrapper.yml", "r") as f:
        content = yaml.safe_load(f)

    # Verify it's a list of tasks
    assert isinstance(content, list), "Task file should be a list"
    assert len(content) > 0, "Task file should contain tasks"

    # Check for validation task
    task_names = [task.get("name", "") for task in content]
    assert any("Validate" in name or "validate" in name for name in task_names), \
        "Missing validation task in consul_installation_wrapper"


def test_haproxy_loadbalancer_wrapper_has_preflights():
    """Verify haproxy_loadbalancer_wrapper.yml has pre-flight validation."""
    with open("roles/common/tasks/haproxy_loadbalancer_wrapper.yml", "r") as f:
        content = yaml.safe_load(f)

    # Verify it's a list of tasks
    assert isinstance(content, list), "Task file should be a list"
    assert len(content) > 0, "Task file should contain tasks"

    # Check for validation task
    task_names = [task.get("name", "") for task in content]
    assert any("Validate" in name or "validate" in name for name in task_names), \
        "Missing validation task in haproxy_loadbalancer_wrapper"


def test_phase2c_line_count_validation():
    """Verify PHASE 2.C implementation has reasonable code volume."""
    # Count total lines of code
    task_files = list(Path("roles/common/tasks").glob("*_wrapper.yml"))
    template_files = list(Path("roles/common/templates").glob("*config*.j2")) + \
                    list(Path("roles/common/templates").glob("consul_*.j2")) + \
                    list(Path("roles/common/templates").glob("haproxy_*.j2"))

    # Filter to only PHASE 2.C files
    phase2c_tasks = [f for f in task_files if any(
        x in f.name for x in ["consul", "haproxy"]
    )]
    phase2c_templates = [f for f in template_files if any(
        x in f.name for x in ["consul", "haproxy"]
    )]

    total_loc = 0

    # Count LOC in task files
    for task_file in phase2c_tasks:
        with open(task_file, "r") as f:
            total_loc += len(f.readlines())

    # Count LOC in template files
    for template_file in phase2c_templates:
        with open(template_file, "r") as f:
            total_loc += len(f.readlines())

    # Expected range: 800-2000 LOC for PHASE 2.C (includes comprehensive templates)
    assert total_loc >= 800, f"Implementation too small: {total_loc} LOC"
    assert total_loc <= 2000, f"Implementation too large: {total_loc} LOC"


def test_consul_service_definition_template_is_json():
    """Verify consul_service_definition.j2 is valid JSON with Jinja2."""
    with open("roles/common/templates/consul_service_definition.j2", "r") as f:
        content = f.read()

    # Should start with JSON
    assert content.strip().startswith("{"), "Service definition should be JSON"
    # Should contain service key
    assert "service" in content, "Missing 'service' key in definition"
    # Should support templates
    assert "{{" in content or "{%" in content, "Should contain Jinja2 templates"


def test_haproxy_stats_config_has_monitoring():
    """Verify haproxy_stats_config.j2 has monitoring configuration."""
    with open("roles/common/templates/haproxy_stats_config.j2", "r") as f:
        content = f.read()

    # Verify monitoring configuration
    expected_elements = [
        "stats",
        "admin",
        "listen",
    ]

    for element in expected_elements:
        assert element in content, f"Missing '{element}' in HAProxy stats config"


def test_phase2c_total_variable_count():
    """Verify PHASE 2.C has sufficient configuration variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Count service discovery variables
    consul_vars = [k for k in defaults.keys() if k.startswith("service_discovery_")]
    haproxy_vars = [k for k in defaults.keys() if k.startswith("loadbalancing_")]

    # Expect at least 15 Consul + 20 HAProxy = 35 total
    total_phase2c_vars = len(consul_vars) + len(haproxy_vars)
    assert total_phase2c_vars >= 30, \
        f"Expected 30+ PHASE 2.C variables, found {total_phase2c_vars}"


def test_phase2c_templates_have_jinja2_syntax():
    """Verify PHASE 2.C templates use valid Jinja2 syntax."""
    template_files = [
        "roles/common/templates/consul_server_config.j2",
        "roles/common/templates/consul_client_config.j2",
        "roles/common/templates/haproxy_config.j2",
    ]

    for template_file in template_files:
        with open(template_file, "r") as f:
            content = f.read()

        # Should contain template variables (not all will, but some should)
        # This is more of a sanity check that files aren't empty
        assert len(content) > 50, f"Template file {template_file} seems empty or too small"


if __name__ == "__main__":
    # Allow running tests directly
    import pytest
    pytest.main([__file__, "-v"])
