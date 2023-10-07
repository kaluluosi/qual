# 开发命令行工具，类似 django的项目的那个工具
# TODO: 尽量将项目开发用的工具命令全部做到cli中，跨平台使用
# XXX: 不知道这个CLI能不能跟具体项目剥离

import click
from sqlalchemy_utils import database_exists, create_database, drop_database
from qual.core.database import engine  # <- 因为这里导入了所以引擎初始化了， XXX：cli无法剥离因为这里耦合了
from qual.core.xyapi.auto_discover import auto_discover
from alembic.config import main as alembic_main


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

    # TODO: 自动发现所有 seeder 模块，然后执行 seeder
    # XXX: `seeder` 种子数据在 `ruby on rails` 中是很重要的一个功能，因为后端项目
    # 运行还依赖了大量的数据库初始数据，需要一个工具来发现和执行填充种子数据。
    auto_discover("qual", "__seed__")


@main.command
def seed():
    """
    填充种子数据（数据库初始数据）
    """
    auto_discover("qual", "__seed__")
