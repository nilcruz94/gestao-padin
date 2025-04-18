"""Adicionando campo conferido nas tabelas

Revision ID: 4998fb41208b
Revises: ccfff68c77d4
Create Date: 2025-03-07 10:48:14.496100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4998fb41208b'
down_revision = 'ccfff68c77d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('esquecimento_ponto', schema=None) as batch_op:
        batch_op.alter_column('hora_primeira_entrada',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.Time(),
               existing_nullable=True)
        batch_op.alter_column('hora_primeira_saida',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.Time(),
               existing_nullable=True)
        batch_op.alter_column('hora_segunda_entrada',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.Time(),
               existing_nullable=True)
        batch_op.alter_column('hora_segunda_saida',
               existing_type=sa.VARCHAR(length=5),
               type_=sa.Time(),
               existing_nullable=True)
        batch_op.drop_constraint('esquecimento_ponto_user_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('tre_total',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.alter_column('tre_usufruidas',
               existing_type=sa.INTEGER(),
               nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.alter_column('cpf',
               existing_type=sa.VARCHAR(length=14),
               nullable=False)
        batch_op.alter_column('rg',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('orgao_emissor',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('orgao_emissor',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               existing_nullable=True)
        batch_op.alter_column('rg',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('cpf',
               existing_type=sa.VARCHAR(length=14),
               nullable=True)
        batch_op.alter_column('tre_usufruidas',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))
        batch_op.alter_column('tre_total',
               existing_type=sa.INTEGER(),
               nullable=False,
               existing_server_default=sa.text('0'))

    with op.batch_alter_table('esquecimento_ponto', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('esquecimento_ponto_user_id_fkey', 'user', ['user_id'], ['id'], ondelete='CASCADE')
        batch_op.alter_column('hora_segunda_saida',
               existing_type=sa.Time(),
               type_=sa.VARCHAR(length=5),
               existing_nullable=True)
        batch_op.alter_column('hora_segunda_entrada',
               existing_type=sa.Time(),
               type_=sa.VARCHAR(length=5),
               existing_nullable=True)
        batch_op.alter_column('hora_primeira_saida',
               existing_type=sa.Time(),
               type_=sa.VARCHAR(length=5),
               existing_nullable=True)
        batch_op.alter_column('hora_primeira_entrada',
               existing_type=sa.Time(),
               type_=sa.VARCHAR(length=5),
               existing_nullable=True)

    # ### end Alembic commands ###
