import pymysql

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """
    获取数据库连接
    g是一个特殊对象，独立于每一个请求。在处理请求过程中，
    它可以用于储存可能多个函数都会用到的数据。把连接储存于其中，可以多次使用，
    而不用在同一个请求中每次调用 get_db 时都创建一个新的连接。
    """
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["DATABASE_HOST"],
            user=current_app.config["DATABASE_USER"],
            password=current_app.config["DATABASE_PASSWORD"],
            db=current_app.config["DATABASE_NAME"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        statements = f.read().decode('utf8').split(';')
        for statement in statements:
            if statement.strip() != '':
                with db.cursor() as cursor:
                    cursor.execute(statement)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")
