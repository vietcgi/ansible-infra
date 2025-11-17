"""
Tests for PHASE 2.D Security & PKI Infrastructure

This module validates the PHASE 2.D implementation with HashiCorp Vault.
Tests ensure proper integration of secrets management, PKI infrastructure, and credential rotation.
"""

import os
import yaml
from pathlib import Path


def test_phase2d_wrapper_tasks_exist():
    """Verify all PHASE 2.D wrapper task files exist."""
    task_files = [
        "roles/common/tasks/vault_installation_wrapper.yml",
        "roles/common/tasks/vault_pki_wrapper.yml",
        "roles/common/tasks/vault_secrets_rotation_wrapper.yml",
    ]
    for task_file in task_files:
        assert Path(task_file).exists(), f"Missing task file: {task_file}"


def test_phase2d_templates_exist():
    """Verify all PHASE 2.D template files exist."""
    template_files = [
        "roles/common/templates/vault_server_config.j2",
        "roles/common/templates/vault_pki_config.j2",
        "roles/common/templates/vault_systemd_service.j2",
        "roles/common/templates/vault_audit_config.j2",
        "roles/common/templates/vault_auth_config.j2",
        "roles/common/templates/vault_logrotate.j2",
        "roles/common/templates/vault_tls_config.j2",
        "roles/common/templates/vault_root_ca_config.j2",
        "roles/common/templates/vault_intermediate_ca_config.j2",
        "roles/common/templates/vault_certificate_templates.j2",
        "roles/common/templates/vault_certificate_renewal.j2",
        "roles/common/templates/vault_crl_ocsp_config.j2",
        "roles/common/templates/vault_database_rotation.j2",
        "roles/common/templates/vault_ssh_rotation.j2",
        "roles/common/templates/vault_api_key_rotation.j2",
        "roles/common/templates/vault_rotation_policies.j2",
        "roles/common/templates/vault_rotation_job.sh.j2",
        "roles/common/templates/vault_rotation_monitoring.j2",
        "roles/common/templates/vault_rotation_audit.j2",
    ]
    for template_file in template_files:
        assert Path(template_file).exists(), f"Missing template file: {template_file}"


def test_phase2d_task_files_valid_yaml():
    """Verify all PHASE 2.D task files are valid YAML."""
    task_files = [
        "roles/common/tasks/vault_installation_wrapper.yml",
        "roles/common/tasks/vault_pki_wrapper.yml",
        "roles/common/tasks/vault_secrets_rotation_wrapper.yml",
    ]

    for task_file in task_files:
        with open(task_file, "r") as f:
            try:
                yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {task_file}: {e}")


def test_defaults_main_yml_contains_vault_core_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault core variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault core variables
    vault_core_vars = [
        "security_vault_enabled",
        "security_vault_version",
        "security_vault_download_url",
        "security_vault_user",
        "security_vault_group",
    ]

    for var in vault_core_vars:
        assert var in defaults, f"Missing Vault core variable: {var}"


def test_defaults_main_yml_contains_vault_network_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault network variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault network variables
    vault_network_vars = [
        "security_vault_bind_addr",
        "security_vault_advertise_addr",
        "security_vault_http_port",
        "security_vault_https_port",
        "security_vault_cluster_port",
    ]

    for var in vault_network_vars:
        assert var in defaults, f"Missing Vault network variable: {var}"


def test_defaults_main_yml_contains_vault_storage_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault storage variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault storage variables
    vault_storage_vars = [
        "security_vault_storage_backend",
        "security_vault_storage_path",
        "security_vault_storage_consul_addr",
        "security_vault_storage_consul_path",
    ]

    for var in vault_storage_vars:
        assert var in defaults, f"Missing Vault storage variable: {var}"


def test_defaults_main_yml_contains_vault_ha_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault HA variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault HA variables
    vault_ha_vars = [
        "security_vault_ha_enabled",
        "security_vault_ha_node_count",
        "security_vault_ha_cluster_name",
    ]

    for var in vault_ha_vars:
        assert var in defaults, f"Missing Vault HA variable: {var}"


def test_defaults_main_yml_contains_vault_unsealing_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault unsealing variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault unsealing variables
    vault_unsealing_vars = [
        "security_vault_auto_unseal_enabled",
        "security_vault_seal_type",
        "security_vault_seal_key_shares",
        "security_vault_seal_key_threshold",
    ]

    for var in vault_unsealing_vars:
        assert var in defaults, f"Missing Vault unsealing variable: {var}"


def test_defaults_main_yml_contains_vault_tls_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault TLS variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault TLS variables
    vault_tls_vars = [
        "security_vault_tls_enabled",
        "security_vault_tls_cert_file",
        "security_vault_tls_key_file",
        "security_vault_tls_ca_file",
        "security_vault_tls_client_auth",
    ]

    for var in vault_tls_vars:
        assert var in defaults, f"Missing Vault TLS variable: {var}"


def test_defaults_main_yml_contains_vault_audit_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault audit variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault audit variables
    vault_audit_vars = [
        "security_vault_audit_enabled",
        "security_vault_audit_log_path",
        "security_vault_audit_retention_days",
        "security_vault_audit_hmac_accessor",
    ]

    for var in vault_audit_vars:
        assert var in defaults, f"Missing Vault audit variable: {var}"


def test_defaults_main_yml_contains_vault_pki_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault PKI variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault PKI variables
    vault_pki_vars = [
        "security_vault_pki_enabled",
        "security_vault_pki_max_lease_ttl",
        "security_vault_pki_default_ttl",
        "security_vault_pki_root_ca_ttl",
        "security_vault_pki_intermediate_ca_ttl",
        "security_vault_pki_crl_expiry",
        "security_vault_pki_roles",
    ]

    for var in vault_pki_vars:
        assert var in defaults, f"Missing Vault PKI variable: {var}"


def test_defaults_main_yml_contains_vault_rotation_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault rotation variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault rotation variables
    vault_rotation_vars = [
        "security_vault_database_rotation_enabled",
        "security_vault_database_rotation_interval",
        "security_vault_database_static_role_rotation_period",
        "security_vault_ssh_rotation_enabled",
        "security_vault_api_key_rotation_enabled",
        "security_vault_api_key_rotation_interval",
    ]

    for var in vault_rotation_vars:
        assert var in defaults, f"Missing Vault rotation variable: {var}"


def test_defaults_main_yml_contains_vault_auth_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault auth method variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault auth method variables
    vault_auth_vars = [
        "security_vault_auth_methods",
        "security_vault_secrets_engines",
    ]

    for var in vault_auth_vars:
        assert var in defaults, f"Missing Vault auth variable: {var}"


def test_defaults_main_yml_contains_vault_logging_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault logging variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault logging variables
    vault_logging_vars = [
        "security_vault_log_level",
        "security_vault_log_path",
        "security_vault_log_format",
    ]

    for var in vault_logging_vars:
        assert var in defaults, f"Missing Vault logging variable: {var}"


def test_defaults_main_yml_contains_vault_health_check_variables():
    """Verify defaults/main.yml includes PHASE 2.D Vault health check variables."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check for key Vault health check variables
    vault_health_vars = [
        "security_vault_health_check_enabled",
        "security_vault_health_check_interval",
        "security_vault_health_check_timeout",
    ]

    for var in vault_health_vars:
        assert var in defaults, f"Missing Vault health check variable: {var}"


def test_vault_installation_wrapper_contains_fqcn():
    """Verify vault_installation_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/vault_installation_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - assert:",
        "  - fail:",
        "  - uri:",
        "  - file:",
        "  - copy:",
        "  - template:",
        "  - get_url:",
        "  - unarchive:",
        "  - systemd:",
        "  - service:",
        "  - apt:",
        "  - yum:",
        "  - user:",
        "  - group:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in vault_installation_wrapper: {pattern}"


def test_vault_pki_wrapper_contains_fqcn():
    """Verify vault_pki_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/vault_pki_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - assert:",
        "  - fail:",
        "  - uri:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in vault_pki_wrapper: {pattern}"


def test_vault_secrets_rotation_wrapper_contains_fqcn():
    """Verify vault_secrets_rotation_wrapper.yml uses FQCN for all modules."""
    with open("roles/common/tasks/vault_secrets_rotation_wrapper.yml", "r") as f:
        content = f.read()

    # Check for non-FQCN module usage (basic check)
    forbidden_patterns = [
        "  - command:",
        "  - shell:",
        "  - debug:",
        "  - assert:",
        "  - fail:",
        "  - uri:",
    ]

    for pattern in forbidden_patterns:
        assert pattern not in content, f"Found non-FQCN module in vault_secrets_rotation_wrapper: {pattern}"


def test_phase2d_line_count_validation():
    """Verify PHASE 2.D implementation is within expected LOC range."""
    task_files = [
        "roles/common/tasks/vault_installation_wrapper.yml",
        "roles/common/tasks/vault_pki_wrapper.yml",
        "roles/common/tasks/vault_secrets_rotation_wrapper.yml",
    ]

    total_loc = 0
    for task_file in task_files:
        with open(task_file, "r") as f:
            total_loc += len(f.readlines())

    # Expected range: 800-2000 LOC for PHASE 2.D wrapper tasks
    assert total_loc >= 800, f"PHASE 2.D wrapper tasks too small: {total_loc} LOC"
    assert total_loc <= 2000, f"PHASE 2.D wrapper tasks too large: {total_loc} LOC"


def test_phase2d_templates_line_count_validation():
    """Verify PHASE 2.D template files are properly sized."""
    template_files = [
        "roles/common/templates/vault_server_config.j2",
        "roles/common/templates/vault_pki_config.j2",
        "roles/common/templates/vault_systemd_service.j2",
        "roles/common/templates/vault_audit_config.j2",
        "roles/common/templates/vault_auth_config.j2",
        "roles/common/templates/vault_logrotate.j2",
        "roles/common/templates/vault_tls_config.j2",
        "roles/common/templates/vault_root_ca_config.j2",
        "roles/common/templates/vault_intermediate_ca_config.j2",
        "roles/common/templates/vault_certificate_templates.j2",
        "roles/common/templates/vault_certificate_renewal.j2",
        "roles/common/templates/vault_crl_ocsp_config.j2",
        "roles/common/templates/vault_database_rotation.j2",
        "roles/common/templates/vault_ssh_rotation.j2",
        "roles/common/templates/vault_api_key_rotation.j2",
        "roles/common/templates/vault_rotation_policies.j2",
        "roles/common/templates/vault_rotation_job.sh.j2",
        "roles/common/templates/vault_rotation_monitoring.j2",
        "roles/common/templates/vault_rotation_audit.j2",
    ]

    total_template_loc = 0
    for template_file in template_files:
        with open(template_file, "r") as f:
            total_template_loc += len(f.readlines())

    # Expected range: 300-1000 LOC for PHASE 2.D templates
    assert total_template_loc >= 300, f"PHASE 2.D templates too small: {total_template_loc} LOC"
    assert total_template_loc <= 1000, f"PHASE 2.D templates too large: {total_template_loc} LOC"


def test_vault_variables_have_sensible_defaults():
    """Verify PHASE 2.D Vault variables have sensible default values."""
    with open("roles/common/defaults/main.yml", "r") as f:
        defaults = yaml.safe_load(f)

    # Check default port values are reasonable
    assert 1024 <= defaults.get("security_vault_http_port", 0) <= 65535, "HTTP port out of range"
    assert 1024 <= defaults.get("security_vault_https_port", 0) <= 65535, "HTTPS port out of range"
    assert 1024 <= defaults.get("security_vault_cluster_port", 0) <= 65535, "Cluster port out of range"

    # Check version is set
    assert defaults.get("security_vault_version"), "Vault version not set"

    # Check storage path is set
    assert defaults.get("security_vault_storage_path"), "Storage path not set"

    # Check log path is set
    assert defaults.get("security_vault_log_path"), "Log path not set"
