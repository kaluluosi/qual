import click
from qual.core.xyapi.auto_discover import auto_discover


@click.group
def db():
    """
    数据库工具
    """
    ...


@db.command
def seed():
    """
    填充种子数据
    """
    auto_discover("qual", "__seed__")
