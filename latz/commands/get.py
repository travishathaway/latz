import click


@click.command("get")
@click.argument("search")
@click.pass_context
def command(ctx, search: str):
    """
    Command that retrieves an image based on a search term
    """
    config = ctx.obj.config

    print(config.backend)
    print(search)
