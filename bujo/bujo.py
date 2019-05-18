import click
import getpass
import os
import yaml
import pysnooper
from pprint import pprint as pp

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


# TODO - Figure out why only top bujo is being printed if a nested one is below it
def show_bujo():
    """Displays all bujo's"""
    data = _yaml_r() or {}
    bujos = sorted([bujo for bujo in data])
    title = Figlet(font='slant')
    if data:
        for k, v in data.items():
            if type(v) is not dict:
                click.echo(click.style(k, fg='magenta'))
                for index, item in enumerate(v, start=1):#
                    click.echo(click.style("  {}  {}".format(str(index), item)))
                break
            click.echo("")
            click.echo(click.style(k, fg='magenta'))
            for k1, v1, in v.items():
                click.echo(click.style("- {}".format(k1), fg='green'))
                for index, item in enumerate(v1, start=1):
                    click.echo(click.style("  {}  {}".format(str(index), item)))
                click.echo("")
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
@click.option('--words', '-w', help='The custom text to print', metavar='<str>')
@click.option('--color', '-c', help='The color to print in')
def fig(words, color='black'):
    """Prints PyBujo or a cool message"""
    f = Figlet(font='slant')
    if words:
        click.echo(click.style(f.renderText(words), fg=color))
    else:
        click.echo(click.style(f.renderText(getpass.getuser()), fg=color))


@cli.command()
@click.argument('note', type=str)
@click.option('-b', '--bujo', help='The name of the new journal to create', metavar='<str>')
def add(note, bujo=None):
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
        click.echo(click.style('There is no note at index {} in {}'.format(index, bujo), fg='red'))
        return
    else:
        if data[bujo] is None:
            del data[bujo]
        _yaml_w(data)


@cli.command()
@click.argument('from_bujo', type=str)
@click.option('--fromnested', '-fb', default=False, type=str)
@click.argument('to_bujo', type=str)
@click.option('--tonested', '-tb', default=False, type=str)
@click.argument('index', type=int)
@pysnooper.snoop()
def mv(from_bujo, to_bujo, index, from_nested_bujo=None, to_nested_bujo=None):
    data = _yaml_r()
    f_bujo = from_bujo.title()
    t_bujo = to_bujo.title()
    if from_nested_bujo:
        f_n_bujo = from_nested_bujo.title()
    if to_nested_bujo:
        t_n_bujo = to_nested_bujo.title()

    try:
        if f_n_bujo:
            del data[f_bujo][f_n_bujo]
        else:
            del data[f_bujo]
    except (KeyError, IndexError, TypeError):
        if f_n_bujo:
            click.echo(click.style('There is no note at index {} in {} - {}'.format(
                index, f_bujo, f_n_bujo), fg='red'))
        else:
            click.echo(click.style('There is no note at index {} in {}'.format(index, f_bujo), fg='red'))
        return
    else:
        to_position = data[t_bujo][t_n_bujo] if t_n_bujo else data[t_bujo]
        from_position = data[f_bujo][f_n_bujo] if f_n_bujo else data[f_bujo]
        if index in to_position:
            click.echo(click.style('This note already exists in {}'.format(t_bujo), fg='red'))
            return
        else:
            to_position.append(index)
        if data[f_bujo] is None:
            del from_position
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

