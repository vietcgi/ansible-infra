"""
Tests for PHASE 3 Disaster Recovery & Backup Automation

This module validates the disaster recovery and backup automation wrapper
with comprehensive backup strategies, failover automation, and recovery procedures.
"""

import os
import yaml
from pathlib import Path


def test_disaster_recovery_wrapper_file_exists():
    """Verify disaster recovery wrapper task file exists."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    assert Path(wrapper_file).exists(), f"Missing disaster recovery wrapper: {wrapper_file}"


def test_disaster_recovery_wrapper_yaml_valid():
    """Verify disaster recovery wrapper YAML is valid."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        try:
            yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise AssertionError(f"Invalid YAML in {wrapper_file}: {e}")


def test_disaster_recovery_wrapper_fqcn_compliance():
    """Verify disaster recovery wrapper uses FQCN for all modules."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    # Check for use of FQCN modules
    assert "ansible.builtin" in content or "kubernetes.core" in content, \
        "Disaster recovery wrapper should use FQCN modules"


def test_disaster_recovery_wrapper_contains_required_sections():
    """Verify disaster recovery wrapper contains all required sections."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    required_sections = [
        "Validate disaster recovery prerequisites",
        "Create backup storage directories",
        "Setup backup encryption keys",
        "Create etcd backup script",
        "Create application backup script",
        "Create persistent volume backup script",
        "Schedule automated backups via cron",
        "Setup backup replication",
        "Create disaster recovery runbook",
        "Configure automated database failover",
        "Setup health check monitoring",
        "Create backup status monitoring dashboard",
    ]

    for section in required_sections:
        assert section in content, f"Missing required section: {section}"


def test_disaster_recovery_defaults_variables_exist():
    """Verify defaults/main.yml includes disaster recovery variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for disaster recovery core variables
    dr_vars = [
        "disaster_recovery_enabled",
        "backup_storage_path",
        "disaster_recovery_rto",
        "disaster_recovery_rpo",
        "disaster_recovery_backup_retention",
        "disaster_recovery_encryption_enabled",
        "disaster_recovery_etcd_backup_enabled",
        "disaster_recovery_automated_failover_enabled",
    ]

    for var in dr_vars:
        assert var in defaults, f"Missing disaster recovery variable: {var}"


def test_disaster_recovery_variables_sensible_defaults():
    """Verify disaster recovery variables have sensible defaults."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check RTO/RPO are set
    rto = defaults.get("disaster_recovery_rto")
    assert rto, "RTO should be set"
    assert "hour" in rto or "minute" in rto, f"RTO should include time unit: {rto}"

    rpo = defaults.get("disaster_recovery_rpo")
    assert rpo, "RPO should be set"
    assert "hour" in rpo or "minute" in rpo, f"RPO should include time unit: {rpo}"

    # Check backup retention is positive
    retention = defaults.get("disaster_recovery_backup_retention")
    assert retention > 0, "Backup retention should be positive"

    # Check encryption is enabled by default
    encryption = defaults.get("disaster_recovery_encryption_enabled")
    assert encryption is True, "Encryption should be enabled by default"


def test_disaster_recovery_backup_types():
    """Verify all backup types are configured."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    backup_types = [
        "disaster_recovery_etcd_backup_enabled",
        "disaster_recovery_application_backup_enabled",
        "disaster_recovery_pv_snapshots_enabled",
        "disaster_recovery_database_backup_enabled",
    ]

    for backup_type in backup_types:
        assert backup_type in defaults, f"Missing backup type variable: {backup_type}"
        assert isinstance(defaults[backup_type], bool), f"{backup_type} should be boolean"


def test_disaster_recovery_failover_configuration():
    """Verify failover configuration is present."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    failover_vars = [
        "disaster_recovery_automated_failover_enabled",
        "disaster_recovery_failover_check_interval",
        "disaster_recovery_failover_timeout",
    ]

    for var in failover_vars:
        assert var in defaults, f"Missing failover variable: {var}"

    # Check intervals are positive
    check_interval = defaults.get("disaster_recovery_failover_check_interval")
    assert check_interval > 0, "Failover check interval should be positive"


def test_disaster_recovery_wrapper_backup_scripts():
    """Verify disaster recovery wrapper includes backup scripts."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    required_scripts = [
        "backup-etcd.sh",
        "backup-applications.sh",
        "backup-pvs.sh",
        "monitor-failover.sh",
        "backup-status.sh",
    ]

    for script in required_scripts:
        assert script in content, f"Missing backup script: {script}"


def test_disaster_recovery_recovery_procedures():
    """Verify disaster recovery runbook is included."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    # Check for recovery procedures documentation
    assert "RECOVERY_PROCEDURES" in content, "Should include recovery procedures documentation"
    assert "Single Node Failure Recovery" in content or "recovery" in content.lower(), \
        "Should document recovery procedures"


def test_disaster_recovery_wrapper_in_tasks_main():
    """Verify disaster recovery wrapper is imported in tasks/main.yml."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    assert "disaster_recovery_wrapper.yml" in content, \
        "Missing disaster recovery wrapper import in tasks/main.yml"


def test_disaster_recovery_integration_ordering():
    """Verify disaster recovery wrapper is imported at correct order."""
    with open("roles/common/tasks/main.yml", "r") as f:
        content = f.read()

    k8s_pos = content.find("kubernetes_orchestration_wrapper.yml")
    dr_pos = content.find("disaster_recovery_wrapper.yml")

    assert k8s_pos != -1, "Kubernetes wrapper not found"
    assert dr_pos != -1, "Disaster recovery wrapper not found"

    # Disaster recovery should be after Kubernetes (which it depends on)
    assert k8s_pos < dr_pos, "Disaster recovery should be imported after Kubernetes"


def test_disaster_recovery_wrapper_line_count():
    """Verify disaster recovery wrapper meets minimum LOC requirement."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        loc = len(f.readlines())

    # Disaster recovery wrapper should be substantial (300-700 LOC)
    assert loc >= 300, f"Disaster recovery wrapper too small: {loc} LOC (minimum 300)"
    assert loc <= 800, f"Disaster recovery wrapper too large: {loc} LOC (maximum 800)"


def test_disaster_recovery_variables_count():
    """Verify sufficient disaster recovery variables are defined."""
    with open("roles/common/defaults/main.yml", "r") as f:
        content = f.read()

    # Count disaster_recovery_ prefixed variables
    dr_var_count = content.count("disaster_recovery_")

    # Should have at least 20 disaster recovery variables
    assert dr_var_count >= 20, f"Too few disaster recovery variables: {dr_var_count}"


def test_disaster_recovery_encryption_support():
    """Verify encryption support for backups."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    # Check for encryption support
    assert "openssl enc" in content or "encryption" in content.lower(), \
        "Should support backup encryption"


def test_disaster_recovery_replication_support():
    """Verify backup replication support."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check replication is configured
    replication_vars = [
        "disaster_recovery_backup_replication_enabled",
        "disaster_recovery_backup_replication_method",
        "disaster_recovery_secondary_backup_location",
    ]

    for var in replication_vars:
        assert var in defaults, f"Missing replication variable: {var}"


def test_disaster_recovery_monitoring_alerting():
    """Verify monitoring and alerting configuration."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    monitoring_vars = [
        "disaster_recovery_monitoring_enabled",
        "disaster_recovery_alert_on_backup_failure",
        "disaster_recovery_alert_on_replication_lag",
    ]

    for var in monitoring_vars:
        assert var in defaults, f"Missing monitoring variable: {var}"


def test_disaster_recovery_testing_procedures():
    """Verify disaster recovery testing is configured."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    testing_vars = [
        "disaster_recovery_recovery_testing_enabled",
        "disaster_recovery_recovery_test_frequency",
        "disaster_recovery_recovery_test_environment",
    ]

    for var in testing_vars:
        assert var in defaults, f"Missing testing variable: {var}"


def test_disaster_recovery_error_handling():
    """Verify disaster recovery wrapper has proper error handling."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    # Check for error handling
    assert "block:" in content, "Should have block structure"
    assert "rescue:" in content, "Should have rescue block for error handling"


def test_disaster_recovery_idempotency():
    """Verify disaster recovery wrapper supports idempotent operations."""
    wrapper_file = "roles/common/tasks/disaster_recovery_wrapper.yml"
    with open(wrapper_file, "r") as f:
        content = f.read()

    # Check for idempotent patterns
    assert "state: present" in content, "Should use state: present for idempotency"
    assert "ignore_errors" in content, "Should use ignore_errors for graceful degradation"
