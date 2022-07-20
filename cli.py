import click

from deimic_pi.devices.cli.app import CLIApp


@click.command()
@click.option(
    '--log',
    '-l',
    'log',
    default="",
    show_default=True,
    help="Logging output file"
)
def execute(log: str):
    CLIApp.run(log=log)


if __name__ == '__main__':
    execute()
