# 开发命令行工具，类似 django的项目的那个工具
# TODO: 尽量将项目开发用的工具命令全部做到cli中，跨平台使用
# XXX: 不知道这个CLI能不能跟具体项目剥离

import click
from sqlalchemy_utils import database_exists, create_database, drop_database
from qual.core.database import engine  # <- 因为这里导入了所以引擎初始化了， XXX：cli无法剥离因为这里耦合了
from alembic.config import main as alembic_main
from qual.migrations.seeds import seed as seed_data


@click.group
def main():
    """
    Qual项目运维工具
    """
    ...


@main.command
@click.option("-r", "--reinstall", is_flag=True, help="重装，会删除数据库重新创建")
def install(reinstall: bool):
    """
    安装部署项目
    """

    if database_exists(engine.url):
        if reinstall:
            answer = click.confirm("[警告]下面将会删除数据库，请确定", default=False)
            if answer is False:
                return

            drop_database(engine.url)
            click.echo("清档/删除数据库完毕")
        else:
            click.echo("数据库已经存在，项目已经安装过，终止。")
            return

    create_database(engine.url)
    click.echo("数据库创建完毕")

    click.echo("开始Alembic迁移")
    alembic_main(["upgrade", "head"])


@main.command
def seed():
    """
    填充初始数据
    """
    seed_data()
