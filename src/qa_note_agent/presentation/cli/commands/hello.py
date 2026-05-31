import typer


def hello_command(
    name: str = typer.Option(
        "world",
        "--name",
        "-n",
        help="Name to greet.",
    ),
) -> None:
    """Print a hello message."""
    typer.echo(f"Hello, {name}!")
