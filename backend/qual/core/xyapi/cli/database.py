import click

@click.group
def db():
    ...
    
@db.command
def clear():
    """
    清档
    """
    
    answer = click.confirm("是否删除数据库？",default=False,abort=True)
    
    if answer:
        click.echo("删除数据库")