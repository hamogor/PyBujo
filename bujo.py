import click
import getpass
from pyfiglet import Figlet


@click.group()
def cli():
    pass


@cli.command()
@click.option('--custom', default=False)
def fig(custom):
    """Prints PyBujo or a cool message"""
    f = Figlet(font='slant')
    if custom:
        print(f.renderText(custom))
    else:
        print(f.renderText('PyBujo'))

@cli.command()
@click.option("-n" or "--name", default=False)
def config(name=getpass.getuser()):
    pass


if __name__ == '__main__':
    cli = click.CommandCollection(sources=[cli])
    cli()