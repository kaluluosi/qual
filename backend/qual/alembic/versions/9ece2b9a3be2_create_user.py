"""create_user

Revision ID: 9ece2b9a3be2
Revises: 
Create Date: 2023-09-15 15:16:40.374402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ece2b9a3be2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='用户编号'),
    sa.Column('username', sa.String(), nullable=False, comment='用户名'),
    sa.Column('uid', sa.String(), nullable=False, comment='工号/用户唯一标志'),
    sa.Column('name', sa.String(), nullable=False, comment='姓名'),
    sa.Column('password', sa.LargeBinary(), nullable=False, comment='二进制哈希密码'),
    sa.Column('email', sa.String(), nullable=False, comment='邮箱'),
    sa.Column('mobile', sa.String(), nullable=False, comment='手机号码'),
    sa.Column('last_login_at', sa.DateTime(), nullable=False, comment='最后登录时间'),
    sa.Column('avatar', sa.String(), nullable=False, comment='头像'),
    sa.Column('status', sa.Enum('active', 'inactive', 'pending', 'suspended', 'closed', name='status'), nullable=False, comment='状态'),
    sa.Column('is_staff', sa.Boolean(), nullable=False, comment='是否是雇员'),
    sa.Column('account_type', sa.Enum('local', 'ldap', 'xysso', 'qywx', name='accounttype'), nullable=False, comment='账户类型'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.create_index(op.f('ix_users_uid'), 'users', ['uid'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_uid'), table_name='users')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###