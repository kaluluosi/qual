# 开发命令行工具，类似 django的项目的那个工具

# TODO: 尽量将项目开发用的工具命令全部做到cli中，跨平台使用
# XXX: cli放在这个包里不知道合不合适，因为这意味着在这个`cli`的角度，
# `xyapi` 包以上的包它是不知道的。

import click
from .database import db

@click.group
def main():
    """
    XYAPI项目开发工具
    """
    ...
    
    

main.add_command(db)