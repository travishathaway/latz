from argparse import Namespace

import click

from .commands import get_command
from .config import get_app_config
from .constants import CONFIG_FILES


@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(Namespace)
    app_config = get_app_config(CONFIG_FILES)
    ctx.obj.config = app_config


cli.add_command(get_command)


if __name__ == "__main__":
    cli()
