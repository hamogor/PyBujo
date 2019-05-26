import click
import getpass
import os
import yaml
import sys
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


# TODO - Make boards editable
@cli.command()
@click.argument('board', type=str)
@click.argument('bujos', type=str, nargs=-1)
def board(board, bujos):
    """Creates a new board with all bujos inside it"""
    data = _yaml_r() or {}
    board = board.title()
    try:
        data[board.upper()] = {}
        for bujo in bujos:
            data[board.upper()][bujo.upper()] = [None]
    except (KeyError, TypeError, IndexError):
        _error("Error generating this board")

    _yaml_w(data)
    _success("Created board: {}".format(board))
    for bujo in bujos:
        _print("- {}".format(bujo.title()))


# TODO - Remove non types when enumerating lists instead of just skipping them
@cli.command()
@click.argument('bujo', type=str)
@click.argument('note', type=str, nargs=1)
def add(bujo, note):
    """Creates a new note in the specified bujo"""
    to_add = note
    data = _yaml_r() or {}

    try:
        if data[bujo.upper()]:  # If the bujo specified is actually a board
            _error("'{}' is a board not a bujo!".format(bujo.title()))
            _info("Valid bujo's in {}:".format(bujo.title()))
            for index, item in enumerate(data[bujo.upper()], start=1):
                _print("{} {}".format(str(index), item.title()))
                # TODO - Edit board from add
    except KeyError:
        occurrence_of_bujo = get_occurrence_of_key(data, bujo.upper())

        # Check if there are duplicates
        if occurrence_of_bujo > 1:  # If there are multiple bujos with name bujo
            _error("There are multiple bujo's called '{}'\n".format(bujo.title()))
            bujos = nested_lookup(bujo.upper(), data)

            # Print the duplicates and ask which one is to be added to
            for index, notes in enumerate(bujos, start=1):
                _info("{} {}".format(index, bujo.title()))
                for note in notes:
                    _print("- {}".format(note))

            choice = input("Which bujo would you like '{}' appended to? [{}] ".format(
                note, "".join(str(range(1, index, 1)))))

            if int(choice) > index or int(choice) == 0:
                _error("There isn't a {} bujo named {}".format(ordinal(int(choice)), bujo.title()))
                exit()

            # Find path of that bujo and add to it
            bujo_path = getpath(data, bujos[int(choice)-1])  # Keys needed to traverse
            parent_key = bujo_path[0]  # Top level key
            bujo_data = nested_lookup(parent_key, data)[0]  # List of notes in desired bujo

            if to_add in bujo_data[bujo.upper()]:
                _error("'{}' is already in '{} -> {}'".format(to_add, parent_key.title(), bujo.title()))
                exit()

            bujo_data[bujo.upper()].append(to_add)  # Add to the list
            data[parent_key] = bujo_data  # Put the whole board back in
            _yaml_w(data)  # Write to file
            _success("Added '{}' to {} -> {}".format(note, parent_key.title(), bujo.title()))

        elif occurrence_of_bujo < 1:  # If there are no bujos named bujo
            _error("There are no bujos called '{}'".format(bujo.title()))
            _print("You can make it using 'bujo board {}'".format(bujo.title()))

        elif occurrence_of_bujo == 1:  # If there is only one bujo name bujo
            values = nested_lookup(bujo.upper(), data)
            parent_key = getpath(data, values[0])[0]

            if to_add in values[0]:
                _error("'{}' is already in '{} -> {}'".format(to_add, parent_key.title(), bujo.title()))
                exit()

            values[0].append(note)
            nested_update([data], bujo.upper(), values)
            _yaml_w(data)
            _success("Added '{}' to '{} -> {}'".format(note, parent_key.title(), bujo.title()))


# TODO - Exceptions for rm
@cli.command()
@click.argument('bujo', type=str)
@click.option('note')
@click.option('-rf', '--recursive', is_flag=True)
def rm(bujo, note, recursive=False):
    """Deletes a note from a bujo"""
    data = _yaml_r()
    bujo = bujo.title()

    if recursive:
        for key, value in enumerate(data, start=1):
            if note.upper() in key:
                print("Match")
            else:
                print("no match")
    # Check if board has been passed instead
    try:
        if data[bujo.upper()]:  # If the bujo specified is actually a board
            _error("'{}' is a board not a bujo!".format(bujo.title()))
            _info("Valid bujo's in {}:".format(bujo.title()))

            for index, item in enumerate(data[bujo.upper()], start=1):
                _print("{} {}".format(str(index), item.title()))
            _info("You can remove a whole board or bujo using...")

    except KeyError:
        occurrence_of_bujo = get_occurrence_of_key(data, bujo.upper())

        # Check if bujo exists
        if occurrence_of_bujo == 0:
            _error("Bujo '{}' does not exist or is empty".format(bujo))
            exit()
        elif occurrence_of_bujo == 1:
            values = nested_lookup(bujo.upper(), data)
            if arg_is_int(note):
                if values[0][int(note)]:
                    parent_key = getpath(data, values[0])[0]
                    deleted_value = values[0][int(note) - 1]
                    del values[0][int(note) -1]
                    nested_update([data], bujo.upper(), values)
                    _yaml_w(data)
                    _success("Removed '{}' from '{} -> {}'".format(deleted_value,
                                                                   parent_key.title(),
                                                                   bujo.title()))
            else:
                for index, item in enumerate(values[0]):
                    if item is None:
                        values[0].pop(index)
                    elif note in item:
                        deleted_value = values[0][index]
                        values[0].pop(index)
                        break
                    elif index == len(values[0]):
                        print(index)
                        print(len(values[0]))
                        _error("No note like '{}' in '{}'".format(note, bujo))
                        exit()

                parent_key = getpath(data, values[0])[0]
                nested_update([data], bujo.upper(), values)
                _yaml_w(data)
                _success("Removed '{}' from '{} -> {}'".format(deleted_value,
                                                               parent_key.title(),
                                                               bujo.title()))
        elif occurrence_of_bujo > 1:
            print("more than one")


def getpath(nested_dict, value, prepath=()):
    for k, v in nested_dict.items():
        path = prepath + (k,)
        if v == value: # found value
            return path
        elif hasattr(v, 'items'): # v is a dict
            p = getpath(v, value, path) # recursive call
            if p is not None:
                return p


def _note_is_in_bujo(note, bujo):
    return [s for s in bujo if note in bujo]


def arg_is_int(n):
    try:
        num = int(n)
        return True
    except ValueError:
        return False


def ordinal(n):
    return "%d%s" % (
        n, "tsnrhtdd" [(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

def _error(error_message):
    return click.echo(click.style(error_message, fg='red'))


def _success(success_message):
    return click.echo(click.style(success_message, fg='green'))


def _print(print_message):
    return click.echo(click.style(print_message, fg='magenta'))


def _info(title_message):
    return click.echo(click.style(title_message, fg='yellow'))


def _yaml_r():
    try:
        with open(_BUJO_PATH, 'r') as bujo_file:
            return yaml.safe_load(bujo_file)
    except FileNotFoundError:
        with open(_BUJO_PATH, 'w+'):
            _yaml_r()


def _yaml_w(data):
    with open(_BUJO_PATH, 'w') as bujo_file:
        yaml.dump(data, bujo_file, indent=4, default_flow_style=False)


if __name__ == '__main__':
    cli = click.CommandCollection(sources=[cli])
    cli()
