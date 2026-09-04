"""Initial Phase 1 Schema Migration

Revision ID: 0001_initial_phase1
Revises: 
Create Date: 2026-09-03 19:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_phase1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tenants
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=160), nullable=False, unique=True),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', name='tenant_status_enum'), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_tenants_name', 'tenants', ['name'])

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=True),
        sa.Column('role', sa.Enum('ADMIN', 'MEMBER', 'VIEWER', name='user_role_enum'), nullable=False, server_default='MEMBER'),
        sa.Column('status', sa.Enum('ACTIVE', 'SUSPENDED', 'REVOKED', name='user_status_enum'), nullable=False, server_default='ACTIVE'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('tenant_id', 'email', name='uq_users_tenant_email'),
    )
    op.create_index('ix_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # 3. Auth Sessions
    op.create_table(
        'auth_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.LargeBinary(), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_auth_sessions_user_id', 'auth_sessions', ['user_id'])
    op.create_index('ix_auth_sessions_expires_at', 'auth_sessions', ['expires_at'])

    # 4. Targets
    op.create_table(
        'targets',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('mode', sa.Enum('HOSTED', 'LOCAL_HF', 'AGENT', name='target_mode_enum'), nullable=False),
        sa.Column('endpoint_url', sa.Text(), nullable=True),
        sa.Column('model_ref', sa.String(length=512), nullable=True),
        sa.Column('request_profile', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('status', sa.Enum('PENDING_VALIDATION', 'VERIFIED', 'VALIDATION_FAILED', 'SUSPENDED', name='target_status_enum'), nullable=False, server_default='PENDING_VALIDATION'),
        sa.Column('authorization_confirmed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_validated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('configuration_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('tenant_id', 'name', name='uq_targets_tenant_name'),
    )
    op.create_index('ix_targets_tenant_id', 'targets', ['tenant_id'])
    op.create_index('ix_targets_tenant_status', 'targets', ['tenant_id', 'status'])
    op.create_index('ix_targets_deleted_at', 'targets', ['deleted_at'])

    # 5. Target Credentials
    op.create_table(
        'target_credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('kind', sa.Enum('API_KEY', 'OAUTH', 'AGENT_TOKEN', 'CUSTOM_HEADER', name='credential_kind_enum'), nullable=False),
        sa.Column('ciphertext', sa.LargeBinary(), nullable=False),
        sa.Column('key_version', sa.String(length=64), nullable=False),
        sa.Column('secret_last4', sa.String(length=4), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'REVOKED', 'EXPIRED', name='credential_status_enum'), nullable=False, server_default='ACTIVE'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_target_credentials_target_id', 'target_credentials', ['target_id'])

    # 6. Provenance Records
    op.create_table(
        'provenance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('model_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('data_sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('system_prompt_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('operational_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('evidence_refs', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('identity_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('score_version', sa.String(length=32), nullable=False),
        sa.Column('quality_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('target_id', 'version', name='uq_provenance_target_version'),
    )
    op.create_index('ix_provenance_records_target_id', 'provenance_records', ['target_id'])

    # 7. Benchmark Sources
    op.create_table(
        'benchmark_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('source_type', sa.Enum('EXTERNAL', 'DOMAIN_CUSTOM', 'SYNTHETIC', name='benchmark_source_type_enum'), nullable=False),
        sa.Column('external_ref', sa.String(length=512), nullable=True),
        sa.Column('revision', sa.String(length=512), nullable=True),
        sa.Column('license_text', sa.Text(), nullable=True),
        sa.Column('manifest_hash', sa.String(length=64), nullable=False, unique=True),
        sa.Column('status', sa.Enum('APPROVED', 'PENDING_REVIEW', 'REJECTED', 'DEPRECATED', name='benchmark_source_status_enum'), nullable=False, server_default='APPROVED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('source_type', 'revision', name='uq_benchmark_source_revision'),
    )
    op.create_index('ix_benchmark_sources_manifest_hash', 'benchmark_sources', ['manifest_hash'])

    # 8. Test Cases
    op.create_table(
        'test_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('benchmark_sources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('external_case_ref', sa.String(length=256), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('category', sa.String(length=80), nullable=False),
        sa.Column('subcategory', sa.String(length=80), nullable=False),
        sa.Column('mode', sa.Enum('SINGLE', 'SESSION', name='test_case_mode_enum'), nullable=False, server_default='SINGLE'),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('variables_schema', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('session_script', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('owasp_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('severity_ceiling', sa.Enum('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_level_enum'), nullable=False),
        sa.Column('review_status', sa.Enum('APPROVED', 'PENDING', 'REJECTED', name='review_status_enum'), nullable=False, server_default='APPROVED'),
        sa.Column('language', sa.String(length=32), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('source_id', 'content_hash', name='uq_test_cases_source_content_hash'),
        sa.UniqueConstraint('source_id', 'external_case_ref', name='uq_test_cases_source_external_ref'),
    )
    op.create_index('ix_test_cases_source_id', 'test_cases', ['source_id'])
    op.create_index('ix_test_cases_category', 'test_cases', ['category'])

    # 9. Jobs
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('mode', sa.Enum('QUICK', 'FULL', name='job_mode_enum'), nullable=False),
        sa.Column('state', sa.Enum('CREATED', 'VALIDATING', 'QUEUED', 'RUNNING', 'PAUSING', 'PAUSED', 'RECOVERING', 'AGGREGATING', 'CERTIFYING', 'COMPLETED', 'COMPLETED_WITH_LIMITATIONS', 'CANCELLED', 'FAILED', name='job_state_enum'), nullable=False, server_default='CREATED'),
        sa.Column('config_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('sampling_seed', sa.BigInteger(), nullable=False),
        sa.Column('dataset_manifest', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('judge_config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('scoring_version', sa.String(length=32), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cancel_requested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('total_items >= 0', name='ck_jobs_total_items_nonnegative'),
        sa.CheckConstraint('completed_items >= 0', name='ck_jobs_completed_items_nonnegative'),
        sa.CheckConstraint('failed_items >= 0', name='ck_jobs_failed_items_nonnegative'),
    )
    op.create_index('ix_jobs_tenant_id', 'jobs', ['tenant_id'])
    op.create_index('ix_jobs_target_id', 'jobs', ['target_id'])
    op.create_index('ix_jobs_tenant_state', 'jobs', ['tenant_id', 'state'])

    # 10. Sessions
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('targets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('state', sa.Enum('PENDING', 'RUNNING', 'PAUSED', 'COMPLETED', 'SAFE_TERMINATED', 'HARM_DETECTED', 'BLOCKED', 'FAILED', 'PARTIAL', name='session_state_enum'), nullable=False, server_default='PENDING'),
        sa.Column('script_version', sa.String(length=64), nullable=False),
        sa.Column('current_turn', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_turns', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('history_hash', sa.String(length=64), nullable=True),
        sa.Column('termination_reason', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('current_turn >= 0', name='ck_sessions_current_turn_nonnegative'),
        sa.CheckConstraint('max_turns >= 0', name='ck_sessions_max_turns_nonnegative'),
    )
    op.create_index('ix_sessions_job_state', 'sessions', ['job_id', 'state'])

    # 11. Job Items
    op.create_table(
        'job_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=True),
        sa.Column('turn_number', sa.Integer(), nullable=True),
        sa.Column('state', sa.Enum('PENDING', 'LEASED', 'TARGET_RUNNING', 'TARGET_COMPLETE', 'JUDGING', 'COMPLETE', 'RETRY_WAIT', 'BLOCKED', 'FAILED', 'JUDGE_INVALID', name='job_item_state_enum'), nullable=False, server_default='PENDING'),
        sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('lease_owner', sa.String(length=128), nullable=True),
        sa.Column('lease_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_error', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('attempt_count >= 0', name='ck_job_items_attempt_count_nonnegative'),
    )
    op.create_index('ix_job_items_queue', 'job_items', ['job_id', 'state', 'next_retry_at'])
    op.create_index('ix_job_items_lease', 'job_items', ['state', 'lease_expires_at'])

    # 12. Session Turns
    op.create_table(
        'session_turns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('turn_number', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='turn_role_enum'), nullable=False),
        sa.Column('prompt_text', sa.Text(), nullable=False),
        sa.Column('history_before_hash', sa.String(length=64), nullable=False),
        sa.Column('history_after_hash', sa.String(length=64), nullable=False),
        sa.Column('response_ref', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('state', sa.Enum('PENDING', 'SENT', 'RECEIVED', 'JUDGED', 'FAILED', name='turn_state_enum'), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('session_id', 'turn_number', name='uq_session_turns_turn_number'),
        sa.CheckConstraint('turn_number > 0', name='ck_session_turns_positive_turn'),
    )
    op.create_index('ix_session_turns_session_id', 'session_turns', ['session_id'])

    # 13. Test Results
    op.create_table(
        'test_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('job_items.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sessions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('turn_number', sa.Integer(), nullable=True),
        sa.Column('target_status', sa.Enum('SUCCESS', 'REFUSAL', 'MALFORMED', 'TIMEOUT', 'ERROR', 'BLOCKED', name='target_response_status_enum'), nullable=False),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('response_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('judge_status', sa.Enum('PENDING', 'JUDGED', 'JUDGE_INVALID', 'NOT_EVALUABLE', 'SKIPPED', name='judge_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('verdict', sa.Enum('SAFE', 'UNSAFE', 'AMBIGUOUS', 'NOT_EVALUABLE', name='verdict_enum'), nullable=True),
        sa.Column('severity', sa.Enum('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_level_enum'), nullable=True),
        sa.Column('category', sa.String(length=80), nullable=True),
        sa.Column('owasp_id', sa.String(length=32), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('rubric_version', sa.String(length=64), nullable=True),
        sa.Column('judge_model', sa.String(length=128), nullable=True),
        sa.Column('logical_key', sa.String(length=64), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('logical_key', name='uq_test_results_logical_key'),
    )
    op.create_index('ix_test_results_logical_key', 'test_results', ['logical_key'])
    op.create_index('ix_test_results_job_lookup', 'test_results', ['job_id', 'category', 'severity'])
    op.create_index('ix_test_results_session', 'test_results', ['session_id', 'turn_number'])

    # 14. Result Attempts
    op.create_table(
        'result_attempts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('job_items.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attempt_no', sa.Integer(), nullable=False),
        sa.Column('phase', sa.Enum('TARGET', 'JUDGE', name='attempt_phase_enum'), nullable=False),
        sa.Column('status', sa.Enum('SUCCESS', 'RETRYABLE_ERROR', 'HARD_FAILURE', 'TIMEOUT', name='attempt_status_enum'), nullable=False),
        sa.Column('provider_request_id', sa.Text(), nullable=True),
        sa.Column('error_class', sa.String(length=128), nullable=True),
        sa.Column('error_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('job_item_id', 'attempt_no', 'phase', name='uq_result_attempts_item_attempt_phase'),
    )
    op.create_index('ix_result_attempts_job_item_id', 'result_attempts', ['job_item_id'])

    # 15. Judge Evaluations
    op.create_table(
        'judge_evaluations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('test_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_results.id', ondelete='CASCADE'), nullable=False),
        sa.Column('judge_model', sa.String(length=128), nullable=False),
        sa.Column('rubric_version', sa.String(length=64), nullable=False),
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('verdict', sa.Enum('SAFE', 'UNSAFE', 'AMBIGUOUS', 'NOT_EVALUABLE', name='verdict_enum'), nullable=False),
        sa.Column('severity', sa.Enum('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_level_enum'), nullable=False),
        sa.Column('category', sa.String(length=80), nullable=False),
        sa.Column('owasp_id', sa.String(length=32), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=4, scale=3), nullable=True),
        sa.Column('raw_output_ref', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('test_result_id', 'judge_model', 'rubric_version', name='uq_judge_eval_result_model_rubric'),
    )
    op.create_index('ix_judge_evaluations_test_result_id', 'judge_evaluations', ['test_result_id'])

    # 16. Trace Results
    op.create_table(
        'trace_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('test_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_results.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('trace_id', sa.Text(), nullable=True),
        sa.Column('availability', sa.Enum('AVAILABLE', 'UNAVAILABLE', 'CORRUPT', 'PARTIAL', name='trace_availability_enum'), nullable=False, server_default='AVAILABLE'),
        sa.Column('schema_version', sa.String(length=32), nullable=False, server_default='1.0.0'),
        sa.Column('raw_trace_ref', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quality_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )

    # 17. Trace Stages
    op.create_table(
        'trace_stages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('trace_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('trace_results.id', ondelete='CASCADE'), nullable=False),
        sa.Column('stage_index', sa.Integer(), nullable=False),
        sa.Column('stage_type', sa.Enum('PROMPT', 'RETRIEVAL', 'TOOL_CALL', 'INTERMEDIATE_REASONING', 'OUTPUT_SYNTHESIS', name='trace_stage_type_enum'), nullable=False),
        sa.Column('stage_status', sa.Enum('SUCCESS', 'FAILED', 'MODIFIED', 'SKIPPED', name='trace_stage_status_enum'), nullable=False, server_default='SUCCESS'),
        sa.Column('input_ref', sa.Text(), nullable=True),
        sa.Column('output_ref', sa.Text(), nullable=True),
        sa.Column('tool_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('judge_status', sa.Enum('PENDING', 'JUDGED', 'JUDGE_INVALID', 'NOT_EVALUABLE', 'SKIPPED', name='judge_status_enum'), nullable=False, server_default='PENDING'),
        sa.Column('verdict', sa.Enum('SAFE', 'UNSAFE', 'AMBIGUOUS', 'NOT_EVALUABLE', name='verdict_enum'), nullable=True),
        sa.Column('severity', sa.Enum('NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_level_enum'), nullable=True),
        sa.Column('owasp_id', sa.String(length=32), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('trace_result_id', 'stage_index', name='uq_trace_stages_index'),
    )
    op.create_index('ix_trace_stages_lookup', 'trace_stages', ['trace_result_id', 'stage_index'])

    # 18. Certificates
    op.create_table(
        'certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('certificate_number', sa.String(length=64), nullable=False, unique=True),
        sa.Column('status', sa.Enum('GENERATING', 'READY', 'FAILED', 'SUPERSEDED', name='certificate_status_enum'), nullable=False, server_default='GENERATING'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('identity_score', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('trust_score', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('aer', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('shr', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('cmr', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('coverage_summary', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('category_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('failures', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('limitations', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('formula_versions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('export_ref', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('job_id', 'version', name='uq_certificates_job_version'),
    )
    op.create_index('ix_certificates_job_version', 'certificates', ['job_id', 'version'])

    # 19. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='SET NULL'), nullable=True),
        sa.Column('actor_user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('request_id', sa.String(length=64), nullable=True),
        sa.Column('ip_hash', sa.String(length=64), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_audit_logs_tenant_created', 'audit_logs', ['tenant_id', 'created_at'])
    op.create_index('ix_audit_logs_resource_created', 'audit_logs', ['resource_type', 'resource_id', 'created_at'])

    # 20. Idempotency Keys
    op.create_table(
        'idempotency_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('request_hash', sa.String(length=64), nullable=False),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_body', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id', 'user_id', 'key', name='uq_idempotency_tenant_user_key'),
    )
    op.create_index('ix_idempotency_keys_expires_at', 'idempotency_keys', ['expires_at'])


def downgrade() -> None:
    op.drop_table('idempotency_keys')
    op.drop_table('audit_logs')
    op.drop_table('certificates')
    op.drop_table('trace_stages')
    op.drop_table('trace_results')
    op.drop_table('judge_evaluations')
    op.drop_table('result_attempts')
    op.drop_table('test_results')
    op.drop_table('session_turns')
    op.drop_table('job_items')
    op.drop_table('sessions')
    op.drop_table('jobs')
    op.drop_table('test_cases')
    op.drop_table('benchmark_sources')
    op.drop_table('provenance_records')
    op.drop_table('target_credentials')
    op.drop_table('targets')
    op.drop_table('auth_sessions')
    op.drop_table('users')
    op.drop_table('tenants')
