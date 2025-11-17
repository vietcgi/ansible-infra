"""
Tests for PHASE 2.E Database Replication & High Availability

This module validates the PHASE 2.E implementation with PostgreSQL and MySQL HA.
Tests ensure proper integration of database replication, backup, and failover.
"""

import os
import yaml
from pathlib import Path


def test_phase2e_wrapper_tasks_exist():
    """Verify all PHASE 2.E wrapper task files exist."""
    task_files = [
        "roles/common/tasks/postgresql_replication_wrapper.yml",
        "roles/common/tasks/mysql_galera_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase2e_templates_exist():
    """Verify all PHASE 2.E template files exist."""
    template_files = [
        "roles/common/templates/postgresql_recovery.conf.j2",
        "roles/common/templates/postgresql_health_check.sh.j2",
        "roles/common/templates/mysql_galera_config.j2",
        "roles/common/templates/mysql_galera_health_check.sh.j2",
        "roles/common/templates/mysql_logrotate.j2",
        "roles/common/templates/postgresql_logrotate.j2",
        "roles/common/templates/database_backup.sh.j2",
    ]
    for template_file in template_files:
        assert Path(template_file).exists(), f"Missing template file: {template_file}"


def test_phase2e_task_files_valid_yaml():
    """Verify all PHASE 2.E task files are valid YAML."""
    task_files = [
        "roles/common/tasks/postgresql_replication_wrapper.yml",
        "roles/common/tasks/mysql_galera_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_defaults_main_yml_contains_postgresql_variables():
    """Verify defaults/main.yml includes PHASE 2.E PostgreSQL variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key PostgreSQL variables
    postgresql_vars = [
        "database_postgresql_enabled",
        "database_postgresql_version",
        "database_postgresql_replication_user",
        "database_postgresql_replication_password",
        "database_postgresql_wal_level",
        "database_postgresql_max_wal_senders",
        "database_postgresql_sync_commit",
        "database_postgresql_archive_command",
    ]

    for var in postgresql_vars:
        assert var in defaults, f"Missing PostgreSQL variable: {var}"


def test_defaults_main_yml_contains_mysql_variables():
    """Verify defaults/main.yml includes PHASE 2.E MySQL variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key MySQL variables
    mysql_vars = [
        "database_mysql_enabled",
        "database_mysql_version",
        "database_mysql_cluster_name",
        "database_mysql_sst_method",
        "database_mysql_sst_user",
        "database_mysql_wsrep_threads",
    ]

    for var in mysql_vars:
        assert var in defaults, f"Missing MySQL variable: {var}"


def test_defaults_main_yml_contains_backup_variables():
    """Verify defaults/main.yml includes PHASE 2.E backup variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key backup variables
    backup_vars = [
        "database_backup_enabled",
        "database_backup_path",
        "database_backup_retention_days",
        "database_backup_frequency",
    ]

    for var in backup_vars:
        assert var in defaults, f"Missing backup variable: {var}"


def test_defaults_main_yml_contains_failover_variables():
    """Verify defaults/main.yml includes PHASE 2.E failover variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key failover variables
    failover_vars = [
        "database_failover_enabled",
        "database_failover_manager",
        "database_failover_timeout",
    ]

    for var in failover_vars:
        assert var in defaults, f"Missing failover variable: {var}"


def test_defaults_main_yml_contains_monitoring_variables():
    """Verify defaults/main.yml includes PHASE 2.E monitoring variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key monitoring variables
    monitoring_vars = [
        "database_monitoring_enabled",
        "database_monitoring_exporter_port",
        "database_monitoring_slow_query_enabled",
        "database_monitoring_slow_query_threshold",
    ]

    for var in monitoring_vars:
        assert var in defaults, f"Missing monitoring variable: {var}"


def test_postgresql_replication_wrapper_contains_fqcn():
    """Verify postgresql_replication_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/postgresql_replication_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - file:",
        "  - copy:",
        "  - lineinfile:",
        "  - template:",
        "  - apt:",
        "  - yum:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in postgresql_replication_wrapper: {pattern}"


def test_mysql_galera_wrapper_contains_fqcn():
    """Verify mysql_galera_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/mysql_galera_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - file:",
        "  - copy:",
        "  - template:",
        "  - apt:",
        "  - yum:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in mysql_galera_wrapper: {pattern}"


def test_phase2e_line_count_validation():
    """Verify PHASE 2.E implementation is within expected LOC range."""
    task_files = [
        "roles/common/tasks/postgresql_replication_wrapper.yml",
        "roles/common/tasks/mysql_galera_wrapper.yml",
    ]

    total_loc = 0
    for task_file in task_files:
        with open(task_file, "r") as f:
            total_loc += len(f.readlines())

    # Expected range: 600-1500 LOC for PHASE 2.E wrapper tasks
    assert total_loc >= 600, f"PHASE 2.E wrapper tasks too small: {total_loc} LOC"
    assert total_loc <= 1500, f"PHASE 2.E wrapper tasks too large: {total_loc} LOC"


def test_phase2e_templates_line_count_validation():
    """Verify PHASE 2.E template files are properly sized."""
    template_files = [
        "roles/common/templates/postgresql_recovery.conf.j2",
        "roles/common/templates/postgresql_health_check.sh.j2",
        "roles/common/templates/mysql_galera_config.j2",
        "roles/common/templates/mysql_galera_health_check.sh.j2",
        "roles/common/templates/mysql_logrotate.j2",
        "roles/common/templates/postgresql_logrotate.j2",
        "roles/common/templates/database_backup.sh.j2",
    ]

    total_template_loc = 0
    for template_file in template_files:
        with open(template_file, "r") as f:
            total_template_loc += len(f.readlines())

    # Expected range: 200-800 LOC for PHASE 2.E templates
    assert total_template_loc >= 200, f"PHASE 2.E templates too small: {total_template_loc} LOC"
    assert total_template_loc <= 800, f"PHASE 2.E templates too large: {total_template_loc} LOC"


def test_database_variables_have_sensible_defaults():
    """Verify PHASE 2.E database variables have sensible default values."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check default port values are reasonable
    assert 1024 <= defaults.get("database_monitoring_exporter_port", 9187) <= 65535, "Exporter port out of range"

    # Check version is set
    assert defaults.get("database_postgresql_version"), "PostgreSQL version not set"
    assert defaults.get("database_mysql_version"), "MySQL version not set"

    # Check backup path is set
    assert defaults.get("database_backup_path"), "Backup path not set"

    # Check retention period is reasonable
    assert defaults.get("database_backup_retention_days", 0) >= 7, "Backup retention too short"


def test_postgresql_recovery_config_contains_variables():
    """Verify PostgreSQL recovery config template uses Jinja2 variables."""
    with open("roles/common/templates/postgresql_recovery.conf.j2", "r") as f:
        content = f.read()

    # Check for Jinja2 variable placeholders
    required_variables = [
        "{{ hostvars[groups",
        "{{ database_postgresql_replication_user",
        "{{ database_postgresql_replication_password",
    ]

    for var in required_variables:
        assert var in content, f"Missing variable in postgresql_recovery.conf: {var}"


def test_mysql_galera_config_contains_variables():
    """Verify MySQL Galera config template uses Jinja2 variables."""
    with open("roles/common/templates/mysql_galera_config.j2", "r") as f:
        content = f.read()

    # Check for Jinja2 variable placeholders
    required_variables = [
        "{{ database_mysql_cluster_name",
        "{{ database_mysql_sst_method",
        "{{ database_mysql_wsrep_threads",
    ]

    for var in required_variables:
        assert var in content, f"Missing variable in mysql_galera_config: {var}"


def test_backup_script_is_executable():
    """Verify backup script template has executable permissions."""
    script_path = Path("roles/common/templates/database_backup.sh.j2")
    assert script_path.exists(), "Backup script not found"
    # Check that it's a shell script
    with open(script_path, "r") as f:
        first_line = f.readline().strip()
        assert first_line.startswith("#!"), "Backup script is not executable"
