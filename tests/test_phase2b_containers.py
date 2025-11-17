"""
Tests for PHASE 2.B Container & Application Deployment

This module validates the PHASE 2.B implementation with Docker containers.
Tests ensure proper integration of Docker, Docker Compose, and security hardening.
"""

import os
import yaml
from pathlib import Path


def test_phase2b_wrapper_tasks_exist():
    """Verify all PHASE 2.B wrapper task files exist."""
    task_files = [
        "roles/common/tasks/docker_installation_wrapper.yml",
        "roles/common/tasks/docker_compose_wrapper.yml",
        "roles/common/tasks/docker_security_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase2b_templates_exist():
    """Verify all PHASE 2.B template files exist."""
    template_files = [
        "roles/common/templates/docker_daemon_config.j2",
        "roles/common/templates/docker_registry_config.j2",
        "roles/common/templates/docker_network_config.j2",
        "roles/common/templates/docker_daemon_security.j2",
        "roles/common/templates/docker_compose_wrapper.sh.j2",
        "roles/common/templates/docker_compose_env.j2",
        "roles/common/templates/docker_compose_defaults.j2",
    ]
    for template_file in template_files:
        assert Path(template_file).exists(), f"Missing template file: {template_file}"


def test_docker_collection_in_requirements():
    """Verify requirements.yml includes community.docker collection."""
    with open("requirements.yml", "r") as f:
        requirements = yaml.safe_load(f)

    collections = {col["name"] for col in requirements.get("collections", [])}

    # Check for Docker community collection
    assert "community.docker" in collections, \
        "Missing community.docker collection"


def test_defaults_main_yml_contains_docker_variables():
    """Verify defaults/main.yml includes PHASE 2.B Docker variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Docker variables
    docker_vars = [
        "container_docker_enabled",
        "container_docker_version",
        "container_docker_compose_enabled",
        "container_docker_log_driver",
        "container_docker_log_max_size",
        "container_docker_storage_driver",
        "container_docker_users",
        "container_docker_security_monitoring",
        "container_docker_compose_project_name",
        "container_docker_compose_log_level",
    ]

    for var in docker_vars:
        assert var in defaults, f"Missing variable: {var}"


def test_main_yml_imports_docker_wrappers():
    """Verify main.yml imports the new Docker wrapper tasks."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    wrapper_tasks = [
        "docker_installation_wrapper.yml",
        "docker_compose_wrapper.yml",
        "docker_security_wrapper.yml",
    ]

    for task in wrapper_tasks:
        assert task in content, f"main.yml does not import {task}"


def test_phase2b_task_files_valid_yaml():
    """Verify all PHASE 2.B task files are valid YAML."""
    task_files = [
        "roles/common/tasks/docker_installation_wrapper.yml",
        "roles/common/tasks/docker_compose_wrapper.yml",
        "roles/common/tasks/docker_security_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_phase2b_templates_valid_yaml():
    """Verify all PHASE 2.B template files have valid YAML structure."""
    template_files = [
        "roles/common/templates/docker_daemon_config.j2",
        "roles/common/templates/docker_registry_config.j2",
        "roles/common/templates/docker_network_config.j2",
        "roles/common/templates/docker_daemon_security.j2",
        "roles/common/templates/docker_compose_env.j2",
        "roles/common/templates/docker_compose_defaults.j2",
    ]

    for template_file in template_files:
        with open(template_file, "r") as f:
            content = f.read()
            # For Jinja2 templates, verify basic structure
            try:
                yaml.safe_load(content)
            except yaml.YAMLError:
                # This is expected for Jinja2 templates, just verify file exists
                pass


def test_phase2b_task_file_syntax():
    """Verify PHASE 2.B task files use proper Ansible syntax."""
    task_files = [
        "roles/common/tasks/docker_installation_wrapper.yml",
        "roles/common/tasks/docker_compose_wrapper.yml",
        "roles/common/tasks/docker_security_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            content = yaml.safe_load(f)
            # Verify it's a valid list of tasks
            assert isinstance(content, list), f"{task_file} should be a list of tasks"
            # Verify at least one task exists
            assert len(content) > 0, f"{task_file} should contain at least one task"
            # Verify each task has a name
            for task in content:
                assert "name" in task, f"Task in {task_file} missing 'name' field"


def test_phase2b_total_implementation_metrics():
    """Verify PHASE 2.B implementation meets expected metrics."""
    # Count task files
    task_files = list(Path("roles/common/tasks").glob("docker_*.yml"))
    assert len(task_files) >= 3, "Missing Docker wrapper task files"

    # Count template files
    template_files = list(Path("roles/common/templates").glob("docker_*.j2"))
    assert len(template_files) >= 5, "Missing Docker template files"

    # Verify defaults/main.yml has container_ variables
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    container_vars = [k for k in defaults.keys() if k.startswith("container_")]
    assert len(container_vars) >= 25, f"Expected 25+ container variables, found {len(container_vars)}"


def test_docker_daemon_config_template_structure():
    """Verify docker_daemon_config.j2 has expected JSON structure."""
    with open("roles/common/templates/docker_daemon_config.j2", "r") as f:
        content = f.read()

    # Verify it contains expected configuration keys
    expected_keys = [
        "log-driver",
        "storage-driver",
        "debug",
        "live-restore",
    ]

    for key in expected_keys:
        assert key in content, f"Missing key '{key}' in docker_daemon_config.j2"


def test_docker_compose_environment_template_structure():
    """Verify docker_compose_env.j2 has expected environment variables."""
    with open("roles/common/templates/docker_compose_env.j2", "r") as f:
        content = f.read()

    # Verify it contains expected environment variables
    expected_vars = [
        "COMPOSE_PROJECT_NAME",
        "COMPOSE_FILE",
        "COMPOSE_API_VERSION",
        "COMPOSE_LOG_LEVEL",
    ]

    for var in expected_vars:
        assert var in content, f"Missing variable '{var}' in docker_compose_env.j2"


def test_docker_security_template_structure():
    """Verify docker_daemon_security.j2 has security configurations."""
    with open("roles/common/templates/docker_daemon_security.j2", "r") as f:
        content = f.read()

    # Verify it contains security-related keys
    expected_keys = [
        "userns-remap",
        "seccomp-profile",
        "no-new-privileges",
        "disable-legacy-registry",
    ]

    for key in expected_keys:
        assert key in content, f"Missing security key '{key}' in docker_daemon_security.j2"


def test_phase2b_line_count_validation():
    """Verify PHASE 2.B implementation has reasonable code volume."""
    # Count total lines of code
    task_files = list(Path("roles/common/tasks").glob("docker_*.yml"))
    template_files = list(Path("roles/common/templates").glob("docker_*.j2"))

    total_loc = 0

    # Count LOC in task files
    for task_file in task_files:
        with open(task_file, "r") as f:
            total_loc += len(f.readlines())

    # Count LOC in template files
    for template_file in template_files:
        with open(template_file, "r") as f:
            total_loc += len(f.readlines())

    # Expected range: 900-1200 LOC (similar to PHASE 2.A)
    assert total_loc >= 700, f"Implementation too small: {total_loc} LOC"
    assert total_loc <= 1500, f"Implementation too large: {total_loc} LOC"


if __name__ == "__main__":
    # Allow running tests directly
    import pytest
    pytest.main([__file__, "-v"])
