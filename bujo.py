import click
import getpass
from pyfiglet import Figlet

#bujo new todo -t board
# new todo list -t = type "board"
#bujo todo
#bujo todo tomorrow -l


@click.group()
def cli():
    pass


@cli.command()
@click.option('--custom', '-c', default=False)
def fig(custom):
    """Prints PyBujo or a cool message"""
    f = Figlet(font='slant')
    if custom:
        print(f.renderText(custom))
    else:
        print(f.renderText(getpass.getuser()))

@cli.command()
@click.option("-n" or "--name", default=False)
def config():
    """
    Either opens config file for editing or provides
        options
    """
    pass

def new():
    """
    Creates a new journal
    """
    pass





if __name__ == '__main__':
    cli = click.CommandCollection(sources=[cli])
    cli()