import click
import getpass
import os
import yaml
import pysnooper
from pprint import pprint as pp
from nested_lookup import (nested_lookup, nested_update,
                           get_all_keys, get_occurrence_of_value,
                           get_occurrence_of_key)

yaml.add_representer(type(None), lambda s, _: s.represent_scalar(
                    'tag:yaml.org,2002:null', ''))
_BUJO_PATH = os.path.join(os.path.expanduser('~'), '.bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        show_bujos()


@cli.command()
@click.argument('board', type=str)
@click.argument('bujos', type=str, nargs=-1)
def board(board, bujos):
    """Creates a new board with all bujos inside it"""
    data = _yaml_r() or {}
    board = board.title()
    try:
        data[board] = {}
        for bujo in bujos:
            data[board][bujo.title()] = [None]
    except (KeyError, TypeError, IndexError):
        _error("Error generating this board")

    _yaml_w(data)
    _success("Created board: {}".format(board))
    for bujo in bujos:
        _print("- {}".format(bujo.title()))


@cli.command()
@click.argument('bujo', type=str)
@click.argument('note', type=str, nargs=1)
def add(bujo, note):
    """Creates a new note in the specified bujo"""
    to_add = note
    print(to_add)
    data = _yaml_r() or {}
    occurrence_of_bujo = get_occurrence_of_key(data, bujo.title())

    # Check if there are duplicates
    if occurrence_of_bujo > 1:
        _error("There are multiple bujo's called '{}'\n".format(bujo.title()))
        bujos = nested_lookup(bujo.title(), data)

        # Print the duplicates and ask which one is to be added to
        for index, notes in enumerate(bujos, start=1):
            _title("{} {}".format(index, bujo.title()))
            for note in notes:
                _print("- {}".format(note))

        choice = input("Which bujo would you like '{}' appended to? [{}] ".format(
            note, "".join(str(range(1, index, 1)))))
        if int(choice) > index or int(choice) == 0:
            _error("There isn't a {} bujo named {}".format(ordinal(int(choice)), bujo))
            exit()

        # Find path of that bujo and add to it
        bujo_path = getpath(data, bujos[int(choice)-1])  # Keys needed to traverse
        parent_key = bujo_path[0]  # Top level key
        bujo_data = nested_lookup(parent_key, data)[0]  # List of notes in desired bujo
        bujo_data[bujo.title()].append(to_add)  # Add to the list
        data[parent_key] = bujo_data  # Put the whole board back in
        _yaml_w(data)  # Write to file

    elif occurrence_of_bujo < 1:
        _error("There are no bujos called '{}'".format(bujo.title()))
        _print("You can make it using 'bujo board {}'".format(bujo.title()))


def getpath(nested_dict, value, prepath=()):
    for k, v in nested_dict.items():
        path = prepath + (k,)
        if v == value: # found value
            return path
        elif hasattr(v, 'items'): # v is a dict
            p = getpath(v, value, path) # recursive call
            if p is not None:
                return p


def ordinal(n):
    return "%d%s" % (
        n, "tsnrhtdd" [(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

def _error(error_message):
    return click.echo(click.style(error_message, fg='red'))


def _success(success_message):
    return click.echo(click.style(success_message, fg='green'))


def _print(print_message):
    return click.echo(click.style(print_message, fg='magenta'))


def _title(title_message):
    return click.echo(click.style(title_message, fg='yellow'))


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
