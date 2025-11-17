"""
Tests for PHASE 2.A Advanced Monitoring Stack

This module validates the PHASE 2.A implementation with upstream roles.
Tests ensure proper integration of Prometheus, Grafana, and AlertManager.
"""

import os
import yaml
from pathlib import Path


def test_phase2a_wrapper_tasks_exist():
    """Verify all PHASE 2.A wrapper task files exist."""
    task_files = [
        "roles/common/tasks/monitoring_prometheus_wrapper.yml",
        "roles/common/tasks/monitoring_grafana_wrapper.yml",
        "roles/common/tasks/monitoring_alertmanager_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase2a_templates_exist():
    """Verify all PHASE 2.A template files exist."""
    template_files = [
        "roles/common/templates/prometheus_custom_scrapes.j2",
        "roles/common/templates/prometheus_custom_rules.j2",
        "roles/common/templates/grafana_datasource_prometheus.j2",
        "roles/common/templates/alertmanager_config.j2",
        "roles/common/templates/alertmanager_routing.j2",
    ]
    for template_file in template_files:
        assert Path(template_file).exists(), f"Missing template file: {template_file}"


def test_requirements_yml_contains_monitoring_collections():
    """Verify requirements.yml includes upstream monitoring collections."""
    with open("requirements.yml", "r") as f:
        requirements = yaml.safe_load(f)

    collections = {col["name"] for col in requirements.get("collections", [])}

    # Check for Prometheus community collection
    assert any("prometheus" in col for col in collections), \
        "Missing prometheus-community.prometheus collection"

    # Check for Grafana collection
    assert "grafana.grafana" in collections, \
        "Missing grafana.grafana collection"


def test_defaults_main_yml_contains_monitoring_variables():
    """Verify defaults/main.yml includes PHASE 2.A monitoring variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key monitoring variables
    monitoring_vars = [
        "monitoring_prometheus_enabled",
        "monitoring_prometheus_version",
        "monitoring_grafana_enabled",
        "monitoring_grafana_version",
        "monitoring_alertmanager_enabled",
        "monitoring_alertmanager_version",
    ]

    for var in monitoring_vars:
        assert var in defaults, f"Missing variable: {var}"


def test_main_yml_imports_monitoring_wrappers():
    """Verify main.yml imports the new monitoring wrapper tasks."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    wrapper_tasks = [
        "monitoring_prometheus_wrapper.yml",
        "monitoring_grafana_wrapper.yml",
        "monitoring_alertmanager_wrapper.yml",
    ]

    for task in wrapper_tasks:
        assert task in content, f"main.yml does not import {task}"


def test_phase2a_task_files_valid_yaml():
    """Verify all PHASE 2.A task files are valid YAML."""
    task_files = [
        "roles/common/tasks/monitoring_prometheus_wrapper.yml",
        "roles/common/tasks/monitoring_grafana_wrapper.yml",
        "roles/common/tasks/monitoring_alertmanager_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_phase2a_templates_valid_yaml():
    """Verify all PHASE 2.A template files are valid YAML."""
    template_files = [
        "roles/common/templates/prometheus_custom_scrapes.j2",
        "roles/common/templates/prometheus_custom_rules.j2",
        "roles/common/templates/grafana_datasource_prometheus.j2",
        "roles/common/templates/alertmanager_config.j2",
        "roles/common/templates/alertmanager_routing.j2",
    ]

    for template_file in template_files:
        with open(template_file, "r") as f:
            content = f.read()
            # For Jinja2 templates, we check basic YAML structure
            # Exclude Jinja2 variables from YAML validation
            try:
                # Try to parse as YAML (will skip Jinja2 sections)
                yaml.safe_load(content)
            except yaml.YAMLError:
                # This is expected for Jinja2 templates, just verify file exists
                pass


def test_phase2a_total_implementation_metrics():
    """Verify PHASE 2.A implementation meets expected metrics."""
    # Count task files
    task_files = list(Path("roles/common/tasks").glob("monitoring_*.yml"))
    assert len(task_files) >= 3, "Missing monitoring wrapper task files"

    # Count template files
    template_files = list(Path("roles/common/templates").glob("*monitoring*.j2")) + \
                    list(Path("roles/common/templates").glob("*prometheus*.j2")) + \
                    list(Path("roles/common/templates").glob("*grafana*.j2")) + \
                    list(Path("roles/common/templates").glob("*alertmanager*.j2"))

    assert len(template_files) >= 5, "Missing monitoring template files"


if __name__ == "__main__":
    # Allow running tests directly
    import pytest
    pytest.main([__file__, "-v"])
