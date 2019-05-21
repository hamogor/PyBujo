import click
import getpass
import os
import yaml
import pysnooper
from pprint import pprint as pp
from pyfiglet import Figlet
from nested_lookup import (nested_lookup, nested_update,
                           get_all_keys, get_occurrence_of_value,
                           get_occurrence_of_key)


_BUJO_PATH = os.path.join(os.path.expanduser('~'), 'bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


# TODO - Make every command take which bujo to work on as first argument and pass that context
@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        show_bujo()


# TODO - Sort out indentation
# TODO - Unnested bujo values being appended and printed as nested value
def show_bujo():
    """Displays all bujo's"""
    data = _yaml_r() or {}
    bujos = get_all_keys(data)
    for bujo in bujos:
        notes = nested_lookup(bujo, [data])
        if isinstance(notes[0], dict):
            click.echo(click.style("* {}".format(bujo), fg='yellow'))
        elif isinstance(notes[0], list):
            click.echo(click.style(" - {}".format(bujo), fg='magenta'))
            for index, note in enumerate(notes[0], start=1):
                click.echo(click.style(" {}  {}".format(str(index), note)))
            click.echo("")


@cli.command()
@click.argument('bujo', type=str)
@click.argument('note', type=str)
def add(note, nested=None, bujo=None):
    """
    Adds a note to a bujo, if no bujo is specified
    writes to 'General'
    """
    keys = []
    data = _yaml_r() or {}
    bujo = bujo.title()
    bujos = get_all_keys(data)
    occurrence_of_bujo = get_occurrence_of_key(data, bujo)

    if occurrence_of_bujo > 1 and len(data[bujo]) is 1:  # This check always returns 1, it shouldnt. 
        error("ERROR: Multiple bujos called '{}' detected on top level".format(bujo))
        error("You'll have to rectify this in {}".format(_BUJO_PATH))
        error("")  # Blank Line

    elif occurrence_of_bujo > 1:
        error("Multiple bujos called '{}' detected".format(bujo))
        error("")  # Blank Line
        list_ = nested_lookup(bujo, data)
        for index, li in enumerate(list_, start=1):
            click.echo(click.style("{} {}".format(str(index), bujo), fg='magenta'))
            for item in li:
                click.echo(click.style("- {}".format(item)))
            click.echo("")
        choices = ""
        chosen_bujo = input(
            "Which bujo should '{}' be added to '1/2/..' >> ".format(note))
        # Index chosen_bujo against list_ index then check data for a list that matches and nested update
        # Go look for a dict with a matching list_[chosen_bujo-1] first in data
    elif occurrence_of_bujo is 1:
        list_ = nested_lookup(bujo, data)
        list_[0].append(note)
        nested_update([data], bujo, list_)
    _yaml_w(data)

@cli.command()
@click.argument('bujo', type=str)
def ls(bujo):
    """Lists all notes in a specific bujo"""
    data = _yaml_r() or {}
    bujo = bujo.title()
    try:
        notes = nested_lookup(
            key = bujo,
            document = data,
        )
    except (KeyError, IndexError, TypeError):
        error("Bujo '{}' does not exist".format(bujo))

    click.echo(click.style("- {}".format(bujo), fg='magenta'))
    for index, note in enumerate(notes[0], start=1):
        click.echo(" {}  {}".format(str(index), note))


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


#@cli.command()
#@click.argument('note', type=str)
#@click.option('-b', '--bujo', help='The name of the new journal to create', metavar='<str>')
#def add(note, bujo=None):
#    """
#    Adds a note to a bujo, if no bujo
#    is specified writes to "General"
#
#    """
#    data = _yaml_r() or {}
#
#    if bujo is None:
#        bujo = 'General'
#    else:
#        bujo = bujo.title()
#
#    try:
#        if note not in data[bujo]:
#            data[bujo].append(note)
#            success("'{}' added to '{}'".format(note, bujo))
#        else:
#            error("You've already made this note")
#    except KeyError:
#        data[bujo] = [note]
#
#    _yaml_w(data)


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
        error("There is no note at index {} in {}".format(index, bujo))
        return
    else:
        if data[bujo] is None:
            del data[bujo]
        _yaml_w(data)


@cli.command()
@click.argument('from_bujo', type=str)
@click.argument('to_bujo', type=str)
@click.argument('index', type=int)
def mv(from_bujo, to_bujo, index, nested=None):
    data = _yaml_r()
    f_bujo = from_bujo.title()
    t_bujo = to_bujo.title()

    # nested_lookup returns a nested list
    try:
        from_vals = nested_lookup(f_bujo, data)[0]
    except (KeyError, IndexError, TypeError):
        error("Bujo '{}' does not exist".format(f_bujo))
        return
    try:
        to_vals = nested_lookup(t_bujo, data)[0]
    except (KeyError, IndexError, TypeError):
        error("Bujo '{}' does not exist".format(f_bujo))
        return

    if from_vals[index-1] in to_vals:
        error("Note '{}' already exists in {}!".format(from_vals[index -1], t_bujo))
    else:
        try:
            to_vals.append(from_vals[index-1])  # Add our note to our list
            original_value = from_vals[index-1]
            del from_vals[index-1]  # Delete from the place we got it

            # update the value of the key to that list
            nested_update([data], f_bujo, from_vals)
            nested_update([data], t_bujo, to_vals)
            success("Moved '{}' from '{}' to '{}'".format(original_value, f_bujo, t_bujo))
        except KeyError:
            error("Bujo '{}' does not exist".format(f_bujo))

    _yaml_w(data)


def error(error):
    return click.echo(click.style(error, fg='red'))


def success(success):
    return click.echo(click.style(success, fg='green'))


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

