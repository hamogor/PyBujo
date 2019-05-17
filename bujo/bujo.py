import click
import getpass
import os
import yaml
import pysnooper

from pyfiglet import Figlet

_BUJO_PATH = os.path.join(os.path.expanduser('~'), 'bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


"""
table_data = [
    ['Heading1', 'Heading2'],
    ['row1 column1', 'row1 column2'],
    ['row2 column1', 'row2 column2'],
    ['row3 column1', 'row3 column2']
]

+--------------+--------------+
| Heading1     | Heading2     |
+--------------+--------------+
| row1 column1 | row1 column2 |
| row2 column1 | row2 column2 |
| row3 column1 | row3 column2 |
+--------------+--------------+
"""


@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        show_bujo()


def show_bujo():
    """Displays all bujo's"""
    data = _yaml_r() or {}
    bujos = sorted([bujo for bujo in data])
    title = Figlet(font='slant')

    if data:
        for bujo in bujos:
            print(title.renderText(bujo))
            for index, item in enumerate(data[bujo], start=1):
                print(' '*3 + str(index) + ': ' + item)
    else:
        click.echo(click.style("You don't have any notes saved!", fg='red'))


@cli.command()
@click.argument('bujo', type=str)
def ls(bujo):
    """Lists all notes in a specific bujo"""
    output = []
    data = _yaml_r() or {}
    bujo = bujo.title()
    entries = data.get(bujo)
    title = Figlet(font='slant')

    if data:
        index = 1
        output.append(title.renderText(bujo))
        for item in entries:
            output.append(str(index) + ': ' + item)
            index += 1
        for line in output:
            click.echo(line)
        click.echo('\n')
    else:
        show_bujo()


@cli.command()
@click.option('--words', '-w', default=False, help='The custom text to print',
              metavar='<str>')
@click.option('--color', '-c', default=False, help='The color to print in')
def fig(words, color='black'):
    """Prints PyBujo or a cool message"""
    f = Figlet(font='slant')
    if words:
        click.echo(click.style(f.renderText(words), fg=color))
    else:
        click.echo(click.style(f.renderText(getpass.getuser()), fg=color))


@cli.command()
@click.argument('note', type=str)
@click.option('-b', '--bujo', help='The name of the new journal to create',
              metavar='<str>')
# @click.option('-n', '--nest', help='Add a board inside a board',
#              metavar='<str>')
def add(note, bujo=None, nest=None):
    """
    Adds a note to a bujo, if no bujo
    is specified writes to "General"

    """
    data = _yaml_r() or {}

    if bujo is None:
        bujo = 'General'
    else:
        bujo = bujo.title()

    try:
        if note not in data[bujo]:
            data[bujo].append(note)
            click.echo(click.style('"{}" added to {}'.format(note, bujo), fg='green'))
        else:
            click.echo(click.style("You've already made this note", fg='red'))
    except KeyError:
        data[bujo] = [note]

    _yaml_w(data)


@cli.command()
@click.argument('bujo', type=str)
@click.argument('index', type=int)
def rm(bujo, index):
    """
    Deletes a note from a bujo
    Removes empty bujo's
    :param bujo: The bujo to delete from
    :param index: The index of the note
    :return:
    """
    data = _yaml_r()
    bujo = bujo.title()

    try:
        del data[bujo][index-1]
    except (KeyError, IndexError, TypeError):
        click.echo(click.style('There is no note {} at index {}'.format(bujo, index), fg='red'))
        return
    else:
        if data[bujo] is None:
            del data[bujo]
        _yaml_w(data)


def _yaml_r():
    try:
        with open(_BUJO_PATH, 'r') as bujo_file:
            return yaml.safe_load(bujo_file)
    except FileNotFoundError:
        with open(_BUJO_PATH, 'w+'):
            ...
        _yaml_r()


def _yaml_w(data):
    with open(_BUJO_PATH, 'w') as bujo_file:
        yaml.dump(data, bujo_file, indent=4, default_flow_style=False)


if __name__ == '__main__':
    cli = click.CommandCollection(sources=[cli])
    cli()

