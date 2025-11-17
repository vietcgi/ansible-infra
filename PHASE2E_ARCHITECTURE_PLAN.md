# PHASE 2.E Architecture & Implementation Plan
## Database Replication & High Availability

**Date**: 2025-11-17
**Status**: Architecture Planning - Ready for Implementation
**Token Budget Available**: ~150,000 / 200,000 tokens

---

## Executive Summary

PHASE 2.E implements enterprise-grade database high availability and replication infrastructure, completing the PHASE 2 advanced services layer by addressing the critical data layer requirements.

**Key Objectives**:
- PostgreSQL streaming replication with automatic failover
- MySQL/MariaDB Galera clustering for synchronous replication
- Backup automation enhancement with point-in-time recovery
- Automated failover mechanisms with health-based detection
- Data synchronization verification and consistency checks

**Estimated Effort**: 40-50 engineer-hours
**Estimated LOC**: 700-900
**Estimated Files**: 5-7 wrapper tasks + 5-7 configuration templates

---

## Architecture Overview

### Database Replication Layer

#### PostgreSQL HA Architecture
```
Primary (Master)
 ↓ (streaming replication)
Replica-1 (Standby)
 ↓ (cascading replication - optional)
Replica-2 (Standby)

Failover Manager (Patroni/etcd or pgpool-II)
 ↓ (health checks every 10s)
Automatic promotion on primary failure
```

**Features**:
- Streaming replication for zero data loss
- Cascading replication for read scaling
- Synchronous/asynchronous replication modes
- WAL archiving for point-in-time recovery
- Monitoring integration with Prometheus

#### MySQL/MariaDB HA Architecture
```
Galera Cluster (synchronous multi-master)
├── Node-1 (Primary)
├── Node-2 (Secondary)
└── Node-3 (Secondary)

All nodes synchronized (SST/IST)
Automatic split-brain detection
Quorum-based decision making
```

**Features**:
- Synchronous replication (zero RPO)
- Multi-master architecture
- Automatic node recovery
- Consistent state maintenance
- Load balancing across nodes

---

## Component Breakdown

### 1. Wrapper Task Files (5-7 files)

#### A. PostgreSQL Replication Wrapper
**File**: `postgresql_replication_wrapper.yml`

**Responsibilities**:
- PostgreSQL binary installation and initialization
- Replication user setup with proper permissions
- Primary/Replica server configuration
- Streaming replication parameter tuning
- WAL archiving setup
- Hot standby configuration
- Replication slot management
- Health check endpoint setup

**Key Tasks**:
1. Install PostgreSQL (via package manager or source)
2. Initialize primary database cluster
3. Configure pg_hba.conf for replication
4. Create replication role with LOGIN, REPLICATION privileges
5. Configure recovery.conf on standbys
6. Setup WAL archiving to S3/local storage
7. Enable archive_mode and archive_timeout
8. Configure max_wal_senders and max_wal_level
9. Setup replication slots for failure detection
10. Configure pg_stat_replication monitoring
11. Setup PostgreSQL health check script
12. Enable log_replication_commands for audit

**Variables Integration**:
- `database_postgresql_enabled` - Feature toggle
- `database_postgresql_version` - PG version (15.x)
- `database_postgresql_replication_user` - Replication user
- `database_postgresql_replication_password` - Replication password
- `database_postgresql_wal_level` - WAL level (replica/logical)
- `database_postgresql_max_wal_senders` - Concurrent replicas
- `database_postgresql_sync_commit` - Synchronous mode
- `database_postgresql_archive_command` - WAL archiving

**Output Artifacts**:
- PostgreSQL server running with replication enabled
- Replication user created with proper ACLs
- pg_hba.conf configured for replication
- WAL archiving operational
- Health check endpoint responding

---

#### B. PostgreSQL Failover Manager Wrapper
**File**: `postgresql_failover_wrapper.yml`

**Responsibilities**:
- Failover automation setup (Patroni or pgpool-II)
- Leader election mechanism
- Health check configuration
- Automatic promotion logic
- VIP management (optional, for client redirection)
- Failover event logging
- Recovery from split-brain scenarios

**Key Components**:
1. Install failover manager (Patroni via Python pip or pgpool-II from packages)
2. Configure etcd integration (for Patroni) or pgpool config
3. Setup health check parameters
4. Configure failover constraints (max_pg_wallog_size, timelines)
5. Setup automatic promotion
6. Configure client redirect on failover
7. Setup monitoring/alerting hooks
8. Configure failover event logging
9. Setup watchdog for split-brain prevention
10. Configure recovery target timeline

**Decision Logic**:
- Patroni: Distributed consensus via etcd (recommended for modern setups)
- pgpool-II: Traditional watchdog with IP takeover
- pacemaker: Legacy option for complex scenarios

**Output Artifacts**:
- Failover manager running and healthy
- etcd cluster operational (for Patroni)
- Automatic promotion ready
- Health checks passing
- Client connection strings updated

---

#### C. MySQL/MariaDB Galera Wrapper
**File**: `mysql_galera_wrapper.yml`

**Responsibilities**:
- MySQL/MariaDB installation with Galera plugin
- Galera cluster initialization
- Node joining mechanism
- Cluster state monitoring
- Split-brain detection configuration
- Backups with cluster awareness
- Replication lag monitoring

**Key Tasks**:
1. Install MySQL 8.0+ or MariaDB 10.4+
2. Install Galera wsrep replication provider
3. Configure my.cnf for Galera clustering
4. Setup cluster name and node list
5. Initialize primary node (wsrep_new_cluster)
6. Join secondary nodes (SST - full sync or IST - incremental)
7. Configure SST method (xtrabackup-v2, mariabackup)
8. Setup node weights for quorum preference
9. Configure wsrep_cluster_address
10. Configure wsrep_notify_cmd for event handling
11. Setup myisam_recover (block by default in Galera)
12. Configure garbd (Galera arbitrator) for 2-node clusters
13. Setup replication lag monitoring

**Cluster Initialization**:
```
Node-1: SET GLOBAL wsrep_provider_options="gmcast.listen_addr=tcp://10.0.1.10:4567";
 SET GLOBAL wsrep_cluster_address="gcomm://"; # Bootstrap
Node-2,3: Join cluster (automatic via wsrep_cluster_address)
```

**Output Artifacts**:
- MySQL Galera cluster operational
- All nodes synchronized (wsrep_local_state=Synced)
- SST method configured
- wsrep_incoming_addresses populated
- Quorum maintained with any 2 of 3 nodes

---

#### D. Database Backup & Recovery Wrapper
**File**: `database_backup_recovery_wrapper.yml`

**Responsibilities**:
- Backup strategy setup (incremental + full)
- Point-in-time recovery (PITR) configuration
- Backup verification and restoration testing
- Backup retention policies
- Encryption of backup artifacts
- Backup monitoring and alerting
- Recovery RTO/RPO calculation

**Key Components for PostgreSQL**:
1. Setup pg_basebackup for base backups
2. Configure WAL archiving to object storage (S3/Minio)
3. Setup backup.info files for PITR
4. Configure backup retention (7 full + 30 WAL days)
5. Setup automated backup verification
6. Configure pg_dump for logical backups (daily or weekly)
7. Setup backup decompression and checksum verification
8. Configure restore test procedure (weekly)
9. Setup backup encryption with pgp-util or similar
10. Configure Barman for centralized backup management (optional)

**Key Components for MySQL**:
1. Setup Percona XtraBackup for base backups
2. Configure binary log archiving
3. Setup backup preparation (apply logs)
4. Configure partial backup support
5. Setup backup verification (innochecksum)
6. Configure backup encryption (encryption-key-algorithm)
7. Setup incremental backup chain management
8. Configure Percona Backup for MongoDB (if applicable)
9. Setup backups to remote storage (NFS, S3)
10. Configure backup rotation and cleanup

**Output Artifacts**:
- Full backup created successfully
- Incremental backups operational
- WAL/binary logs archived
- PITR capability verified
- Recovery procedure tested

---

#### E. Database Monitoring & Alerting Wrapper
**File**: `database_monitoring_wrapper.yml`

**Responsibilities**:
- Prometheus exporters setup
- Custom metrics collection
- Alert rule definitions
- Health check endpoint configuration
- Performance monitoring setup
- Slow query logging
- Replication lag alerting

**PostgreSQL Monitoring**:
1. Install postgres_exporter (Prometheus community)
2. Configure connection pooling metrics (pgbouncer_exporter if using pgbouncer)
3. Setup custom queries for business metrics
4. Configure replication lag monitoring (pg_stat_replication)
5. Setup WAL archiver monitoring
6. Configure checkpoint monitoring
7. Setup index usage tracking
8. Configure table bloat monitoring
9. Setup transaction ID (XID) wraparound alerts
10. Configure pg_stat_statements for query analysis

**MySQL Monitoring**:
1. Install mysqld_exporter
2. Configure slow query log
3. Setup replication metrics (show slave status)
4. Configure thread pool monitoring
5. Setup InnoDB compression ratio tracking
6. Configure table lock monitoring
7. Setup buffer pool efficiency metrics
8. Configure Galera-specific metrics (wsrep_replicated, etc.)
9. Setup binary log monitoring
10. Configure connection pool metrics

**Alert Rules** (Prometheus):
```yaml
# Example PostgreSQL alerts
- alert: PostgreSQLReplicationLag
 expr: pg_replication_lag_seconds > 30
 for: 2m

- alert: PostgreSQLWALArchivingFailure
 expr: time() - pg_stat_archiver_last_wal_time > 300

- alert: PostgreSQLConnectionPooling
 expr: pg_stat_activity_count > pg_max_connections * 0.8

# Example MySQL alerts
- alert: MySQLGaleraNodeOutOfSync
 expr: mysql_wsrep_local_state != 4

- alert: MySQLReplicationLag
 expr: mysql_slave_status_seconds_behind_master > 60
```

**Output Artifacts**:
- Exporters registered with Prometheus
- Dashboards created in Grafana
- Alert rules loaded into AlertManager
- Health endpoints functional
- Metrics flowing to time-series DB

---

#### F. Database Encryption & Compliance Wrapper (Optional)
**File**: `database_encryption_wrapper.yml`

**Responsibilities**:
- Transparent Data Encryption (TDE) setup
- SSL/TLS for client connections
- Backup encryption
- Audit logging for compliance

**PostgreSQL TDE**:
- pgcrypto for column-level encryption
- Whole database encryption via dm-crypt (OS level)
- SSL certificates setup
- sql_audit logging

**MySQL TDE**:
- InnoDB keyring for automated key management
- Undo/redo log encryption
- SSL certificate configuration
- Audit logging plugin

---

### 2. Configuration Templates (5-7 templates)

#### A. PostgreSQL Streaming Replication Config
**File**: `postgresql_streaming_replication.j2`

**Content**:
```
# Primary Server postgresql.conf
wal_level = replica
max_wal_senders = {{ database_postgresql_max_wal_senders | default(5) }}
max_replication_slots = {{ database_postgresql_max_replication_slots | default(5) }}
wal_keep_segments = 64
hot_standby = on
archive_mode = on
archive_command = '{{ database_postgresql_archive_command }}'
archive_timeout = 300
synchronous_commit = {{ database_postgresql_sync_commit | default('on') }}
synchronous_standby_names = '*'
log_replication_commands = on

# Replica Server recovery.conf
standby_mode = on
primary_conninfo = 'host=primary.example.com port=5432 user=replication password=...'
restore_command = '...'
recovery_target_timeline = 'latest'
```

**Variables**:
- max_wal_senders (number of concurrent replicas)
- wal_keep_segments (WAL segments to retain)
- archive_command (WAL archiving destination)
- synchronous_commit (sync replication mode)

---

#### B. MySQL Galera Configuration
**File**: `mysql_galera_config.j2`

**Content**:
```
# my.cnf Galera cluster configuration
[mysqld]
wsrep_on = ON
wsrep_provider = /usr/lib/galera/libgalera_smm.so
wsrep_provider_options = "gmcast.listen_addr=tcp://10.0.1.{{ node_id }}:4567"
wsrep_cluster_address = "gcomm://10.0.1.10,10.0.1.11,10.0.1.12"
wsrep_cluster_name = "{{ cluster_name }}"
wsrep_node_address = "10.0.1.{{ node_id }}"
wsrep_node_name = "{{ inventory_hostname }}"
wsrep_sst_method = mariabackup
wsrep_sst_auth = "{{ backup_user }}:{{ backup_password }}"
wsrep_slave_threads = 4
default_storage_engine = InnoDB

binlog_format = ROW
innodb_autoinc_lock_mode = 2
```

---

#### C. Patroni Configuration
**File**: `postgresql_patroni_config.j2`

**Content** (YAML):
```
scope: {{ cluster_name }}
namespace: /service
name: {{ inventory_hostname }}

restapi:
 listen: {{ hostvars[inventory_hostname].ansible_default_ipv4.address }}:8008

etcd:
 hosts:
 {% for etcd_host in groups['etcd'] %}
 - {{ etcd_host }}:2379
 {% endfor %}

postgresql:
 use_pg_rewind: true
 parameters:
 max_wal_senders: {{ database_postgresql_max_wal_senders }}
 wal_level: replica
 hot_standby: true

bootstrap:
 dcs:
 ttl: 30
 loop_wait: 10
 retry_timeout: 10
 maximum_lag_on_failover: 1048576
 postgresql:
 data_dir: /var/lib/postgresql/data
 bin_dir: /usr/lib/postgresql/15/bin
```

---

#### D. pgpool-II Configuration
**File**: `pgpool_config.j2`

**Content**:
```
# pgpool.conf
listen_addresses = '*'
port = 5432
num_init_children = 32
max_pool = 4

# Backend nodes
backend_hostname0 = '{{ primary_host }}'
backend_port0 = 5432
backend_weight0 = 0
backend_hostname1 = '{{ replica1_host }}'
backend_port1 = 5432
backend_weight1 = 1
backend_hostname2 = '{{ replica2_host }}'
backend_port2 = 5432
backend_weight2 = 1

# Health check
health_check_period = 10
health_check_timeout = 20
health_check_user = 'pgpool'

# Failover script
failover_command = '/etc/pgpool-II/failover.sh %d %h %p %D %m %H %M %P %r %R'
```

---

#### E. Backup Script Template
**File**: `database_backup_script.sh.j2`

**Content**:
```bash
#!/bin/bash

# PostgreSQL backup using pg_basebackup
pg_basebackup -h {{ primary_host }} \
 -D {{ backup_path }}/{{ backup_date }} \
 -U replication \
 -P \
 -v \
 -W

# Create backup manifest
echo "Backup-Date: {{ backup_date }}" > {{ backup_path }}/{{ backup_date }}/backup.info
echo "Backup-Type: base" >> {{ backup_path }}/{{ backup_date }}/backup.info
echo "Backup-Mode: {{ backup_mode }}" >> {{ backup_path }}/{{ backup_date }}/backup.info

# Verify backup
pg_verify_builtin_directory /path/to/backup

# Archive to S3
aws s3 sync {{ backup_path }}/{{ backup_date }} \
 s3://{{ backup_bucket }}/postgres/{{ backup_date }}/
```

---

#### F. Monitoring Alerts Configuration
**File**: `database_alerts.j2`

**Content** (Prometheus alert rules):
```yaml
groups:
- name: database_alerts
 interval: 30s
 rules:
 - alert: PostgreSQLReplicationLag
 expr: pg_replication_lag_seconds > 30
 for: 2m
 labels:
 severity: warning
 annotations:
 summary: "PostgreSQL replication lag {{ $value }}s"

 - alert: PostgreSQLWALArchiveFailed
 expr: time() - pg_stat_archiver_last_wal_time > 600
 for: 5m
 labels:
 severity: critical

 - alert: MySQLGaleraNodeLost
 expr: count(mysql_wsrep_local_state == 4) < 2
 for: 1m
 labels:
 severity: critical
```

---

### 3. Configuration Variables (30-40 variables)

#### PostgreSQL Replication Variables (12)
- `database_postgresql_enabled` - Feature toggle
- `database_postgresql_version` - PostgreSQL version (15.x)
- `database_postgresql_bind_address` - Listen address
- `database_postgresql_port` - Port (5432)
- `database_postgresql_replication_user` - Replication user
- `database_postgresql_replication_password` - Replication password
- `database_postgresql_wal_level` - WAL level (replica/logical)
- `database_postgresql_max_wal_senders` - Concurrent replicas (5)
- `database_postgresql_max_replication_slots` - Replication slots (5)
- `database_postgresql_sync_commit` - Synchronous mode (on/local/remote_apply)
- `database_postgresql_archive_command` - WAL archiving command
- `database_postgresql_archive_timeout` - Archive timeout (300s)

#### MySQL/Galera Variables (10)
- `database_mysql_enabled` - Feature toggle
- `database_mysql_version` - MySQL/MariaDB version
- `database_mysql_cluster_name` - Cluster identifier
- `database_mysql_cluster_nodes` - Node list
- `database_mysql_galera_provider` - Galera library path
- `database_mysql_sst_method` - SST method (xtrabackup/mariabackup)
- `database_mysql_wsrep_threads` - Replication threads
- `database_mysql_innodb_autoinc_lock_mode` - Lock mode (2 for Galera)
- `database_mysql_binlog_format` - Binlog format (ROW)
- `database_mysql_backup_user` - Backup user for SST

#### Failover Variables (6)
- `database_failover_manager` - Tool (patroni/pgpool/pacemaker)
- `database_failover_enabled` - Automatic failover toggle
- `database_failover_timeout` - Detection timeout (30s)
- `database_failover_max_lag` - Max WAL lag for promotion (1MB)
- `database_etcd_enabled` - etcd for Patroni
- `database_etcd_cluster_endpoints` - etcd endpoints

#### Backup Variables (8)
- `database_backup_enabled` - Backup toggle
- `database_backup_path` - Local backup directory
- `database_backup_retention_days` - Retention period (30)
- `database_backup_frequency` - Backup schedule (daily/weekly)
- `database_backup_full_schedule` - Full backup schedule (weekly)
- `database_backup_encrypt` - Encryption toggle
- `database_backup_encryption_key` - Encryption key path
- `database_backup_s3_enabled` - S3 archiving toggle
- `database_backup_s3_bucket` - S3 bucket name
- `database_backup_s3_region` - AWS region

#### Monitoring Variables (8)
- `database_monitoring_enabled` - Monitoring toggle
- `database_monitoring_exporter_port` - Exporter port
- `database_monitoring_scrape_interval` - Scrape frequency
- `database_monitoring_slow_query_enabled` - Slow query log
- `database_monitoring_slow_query_threshold` - Threshold (1000ms)
- `database_monitoring_replication_lag_alert` - Lag threshold (30s)
- `database_monitoring_connection_pool_alert` - Connection threshold (80%)
- `database_monitoring_alert_rules_enabled` - Alert rules toggle

---

### 4. Test Suite (12-15 tests)

**File**: `tests/test_phase2e_database_ha.py`

**Test Categories**:

#### Wrapper Task Validation (3)
- test_phase2e_wrapper_tasks_exist
- test_phase2e_templates_exist
- test_phase2e_task_files_valid_yaml

#### Variable Coverage (4)
- test_defaults_main_yml_contains_postgresql_variables
- test_defaults_main_yml_contains_mysql_variables
- test_defaults_main_yml_contains_failover_variables
- test_defaults_main_yml_contains_backup_variables

#### Code Quality (3)
- test_postgres_replication_wrapper_contains_fqcn
- test_mysql_galera_wrapper_contains_fqcn
- test_phase2e_line_count_validation

#### Configuration Validation (2)
- test_postgresql_config_syntax
- test_mysql_config_syntax

#### Integration (2)
- test_replication_variables_integration
- test_backup_monitoring_integration

---

## Task Execution Order

1. **Phase 1: Installation** (2-3 hours)
 - PostgreSQL installation and configuration
 - MySQL/MariaDB installation
 - Failover manager setup (Patroni or pgpool)

2. **Phase 2: Replication Setup** (2-3 hours)
 - Primary/Replica streaming replication
 - Galera cluster initialization
 - Replication verification

3. **Phase 3: Failover Setup** (1-2 hours)
 - Failover manager configuration
 - Health check tuning
 - Automatic promotion testing

4. **Phase 4: Backup & Recovery** (2-3 hours)
 - Backup script deployment
 - Point-in-time recovery testing
 - Backup retention policies

5. **Phase 5: Monitoring & Alerting** (1-2 hours)
 - Exporter installation
 - Prometheus integration
 - Alert rule configuration

---

## RTO/RPO Targets

### PostgreSQL Streaming Replication
- **RPO (Recovery Point Objective)**: ~1 second (streaming WAL)
- **RTO (Recovery Time Objective)**: ~10-30 seconds (promotion + reconnect)
- **Data Loss**: 0 (with synchronous replication)

### MySQL Galera
- **RPO**: 0 (synchronous multi-master)
- **RTO**: ~5-10 seconds (client reconnect to another node)
- **Data Loss**: 0 (no gaps in transaction log)

### Backup-based Recovery
- **RPO**: ~1 hour (full backup + WAL/binary logs)
- **RTO**: ~30-60 minutes (backup download + restore + replay logs)

---

## Success Criteria

- [ ] PostgreSQL primary-replica streaming operational
- [ ] Replica lag < 30 seconds under normal load
- [ ] Automatic failover < 60 seconds
- [ ] MySQL Galera cluster with 3 nodes synchronized
- [ ] Daily backups executing and archiving
- [ ] Point-in-time recovery tested and working
- [ ] Replication lag alerts triggering correctly
- [ ] Recovery procedure documented and tested
- [ ] Prometheus collecting replication metrics
- [ ] Grafana dashboards displaying cluster health

---

## Risk Mitigation

### Synchronization Risks
- **Risk**: Network partition causing split-brain
- **Mitigation**: Quorum-based decision making in Galera; pgpool watchdog

### Data Integrity Risks
- **Risk**: Data corruption propagating to replicas
- **Mitigation**: Checksums enabled; backup verification; PITR capability

### Failover Risks
- **Risk**: False-positive failover triggering promotion
- **Mitigation**: Multiple health check confirmations; alert validation

### Backup Risks
- **Risk**: Backup corruption or loss
- **Mitigation**: Backup verification; encrypted storage; geo-redundant archiving

---

## Dependencies & Integration

### Hard Dependencies
- PostgreSQL 13+ or MySQL 8.0+ / MariaDB 10.4+
- Replication user accounts with proper ACLs
- PHASE 1: Base OS hardening

### Soft Dependencies
- etcd (for Patroni - optional but recommended)
- Prometheus (for monitoring)
- Consul (for service discovery)
- S3/object storage (for backup archiving)

### Integration Points
- **Service Discovery**: Register database endpoints in Consul
- **Monitoring**: Prometheus exporters for metrics
- **Backup Storage**: S3/Minio for off-site archiving
- **Secrets**: Vault for database passwords and backup encryption keys

---

## Future Enhancements

### Phase 3+
1. **Multi-region Replication** - Cross-datacenter database sync
2. **Sharding Framework** - Horizontal scaling for large datasets
3. **Advanced Backup** - Incremental backups, deduplication
4. **Query Optimization** - Slow query analysis and index recommendations
5. **Disaster Recovery** - Automated DR site failover

---

## Estimated Timeline

| Task | Duration | Effort (hours) |
|------|----------|----------------|
| Architecture Design | 1 day | 4 |
| PostgreSQL Implementation | 2 days | 10 |
| MySQL/Galera Implementation | 2 days | 10 |
| Failover Setup | 1 day | 5 |
| Backup & Recovery | 1.5 days | 8 |
| Monitoring & Testing | 1 day | 5 |
| Documentation | 1 day | 3 |
| **Total** | **~9 days** | **45** |

---

## Conclusion

PHASE 2.E provides enterprise-grade database high availability, ensuring zero-downtime deployment, rapid failover, and complete point-in-time recovery capabilities. Following the successful wrapper pattern from previous phases, PHASE 2.E will deliver production-ready database clustering with comprehensive monitoring and automated recovery procedures.

**Next Phase**: PHASE 3 (Advanced Operations) - Platform-as-a-Service automation, advanced networking, compliance frameworks
