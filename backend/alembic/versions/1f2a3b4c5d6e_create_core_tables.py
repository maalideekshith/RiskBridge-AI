"""create core tables

Revision ID: 1f2a3b4c5d6e
Revises:
Create Date: 2026-09-04

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1f2a3b4c5d6e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the core application tables."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "merchants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column("business_type", sa.String(length=100), nullable=False),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_merchants_id", "merchants", ["id"], unique=False)
    op.create_index("ix_merchants_user_id", "merchants", ["user_id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("merchant_id", sa.Integer(), nullable=False),
        sa.Column("payment_reference", sa.String(length=100), nullable=False),
        sa.Column("customer_reference", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("payment_method", sa.String(length=50), nullable=False),
        sa.Column("ip_address", sa.String(length=100), nullable=True),
        sa.Column("device_reference", sa.String(length=255), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("failure_reason", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["merchant_id"],
            ["merchants.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_reference"),
    )
    op.create_index("ix_payments_id", "payments", ["id"], unique=False)
    op.create_index("ix_payments_merchant_id", "payments", ["merchant_id"], unique=False)
    op.create_index(
        "ix_payments_payment_reference",
        "payments",
        ["payment_reference"],
        unique=True,
    )
    op.create_index(
        "ix_payments_customer_reference",
        "payments",
        ["customer_reference"],
        unique=False,
    )
    op.create_index("ix_payments_status", "payments", ["status"], unique=False)
    op.create_index("ix_payments_created_at", "payments", ["created_at"], unique=False)

    op.create_table(
        "refunds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("refund_reference", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refund_reference"),
    )
    op.create_index("ix_refunds_id", "refunds", ["id"], unique=False)
    op.create_index("ix_refunds_payment_id", "refunds", ["payment_id"], unique=False)
    op.create_index(
        "ix_refunds_refund_reference",
        "refunds",
        ["refund_reference"],
        unique=True,
    )
    op.create_index("ix_refunds_status", "refunds", ["status"], unique=False)
    op.create_index("ix_refunds_created_at", "refunds", ["created_at"], unique=False)

    op.create_table(
        "disputes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("payment_id", sa.Integer(), nullable=False),
        sa.Column("dispute_reference", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("evidence_status", sa.String(length=30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["payment_id"],
            ["payments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dispute_reference"),
    )
    op.create_index("ix_disputes_id", "disputes", ["id"], unique=False)
    op.create_index("ix_disputes_payment_id", "disputes", ["payment_id"], unique=False)
    op.create_index(
        "ix_disputes_dispute_reference",
        "disputes",
        ["dispute_reference"],
        unique=True,
    )
    op.create_index("ix_disputes_status", "disputes", ["status"], unique=False)
    op.create_index("ix_disputes_created_at", "disputes", ["created_at"], unique=False)


def downgrade() -> None:
    """Drop the core application tables."""

    op.drop_table("disputes")
    op.drop_table("refunds")
    op.drop_table("payments")
    op.drop_table("merchants")
    op.drop_table("users")
