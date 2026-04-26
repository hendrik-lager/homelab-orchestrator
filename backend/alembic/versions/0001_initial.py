"""initial migration

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('hosts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('host_type', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('last_seen', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('host_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('cred_type', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('encrypted_value', sa.String(length=4096), nullable=False),
        sa.Column('key_fingerprint', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('service_type', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('image', sa.String(length=512), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('last_checked', sa.DateTime(), nullable=True),
        sa.Column('labels', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service_checks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('checked_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('update_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('update_type', sa.String(length=50), nullable=False),
        sa.Column('package_name', sa.String(length=512), nullable=True),
        sa.Column('current_version', sa.String(length=255), nullable=True),
        sa.Column('available_version', sa.String(length=255), nullable=True),
        sa.Column('is_security', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('metric_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False),
        sa.Column('cpu_percent', sa.Float(), nullable=True),
        sa.Column('ram_used_bytes', sa.Integer(), nullable=True),
        sa.Column('ram_total_bytes', sa.Integer(), nullable=True),
        sa.Column('disk_used_bytes', sa.Integer(), nullable=True),
        sa.Column('disk_total_bytes', sa.Integer(), nullable=True),
        sa.Column('load_1m', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_metric_snapshots_host_id'), 'metric_snapshots', ['host_id'], unique=False)
    op.create_index(op.f('ix_metric_snapshots_captured_at'), 'metric_snapshots', ['captured_at'], unique=False)
    op.create_table('alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=True),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('fired_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('notify_email', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scheduled_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('host_id', sa.Integer(), nullable=True),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('last_run', sa.DateTime(), nullable=True),
        sa.Column('last_result', sa.String(length=20), nullable=True),
        sa.Column('next_run', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['host_id'], ['hosts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('scheduled_jobs')
    op.drop_table('alert_rules')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_metric_snapshots_captured_at'), table_name='metric_snapshots')
    op.drop_index(op.f('ix_metric_snapshots_host_id'), table_name='metric_snapshots')
    op.drop_table('metric_snapshots')
    op.drop_table('update_records')
    op.drop_table('service_checks')
    op.drop_table('services')
    op.drop_table('host_credentials')
    op.drop_table('hosts')
