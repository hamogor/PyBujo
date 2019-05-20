import click
import getpass
import os
import yaml
import pysnooper
from pprint import pprint as pp
from nested_lookup import nested_lookup, nested_update

from pyfiglet import Figlet

_BUJO_PATH = os.path.join(os.path.expanduser('~'), 'bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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
                for index, item in enumerate(v, start=1):
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
@click.argument('to_bujo', type=str)
@click.argument('note', type=int)
def mv(from_bujo, to_bujo, note, nested=None):
    data = _yaml_r()
    f_bujo = from_bujo.title()
    t_bujo = to_bujo.title()

    # nested_lookup returns a nested list
    from_vals = nested_lookup(f_bujo, data)[0]
    to_vals = nested_lookup(t_bujo, data)[0]

    if from_vals[note-1] in to_vals:
        click.echo(click.style("Note '{}' already exists in {}!".format(from_vals, t_bujo), fg='red'))
    else:
        try:
            to_vals.append(from_vals[note-1])  # Add our note to our list
            del from_vals[note-1]  # Delete from the place we got it

            # update the value of the key to that list
            nested_update([data], f_bujo, from_vals)
            nested_update([data], t_bujo, to_vals)
        except KeyError:
            click.echo(click.style("Bujo '{}' does not exist".format(nested), fg='red'))

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

