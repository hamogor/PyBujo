import click
import re
import time
import curses
import os
import yaml
from curses.textpad import Textbox, rectangle
from pprint import pprint as pp
from pick import pick
from pick import Picker
from nested_lookup import (nested_lookup, nested_update,
                           get_all_keys, get_occurrence_of_value,
                           get_occurrence_of_key)


"""
- Actions
- Display view
"""

yaml.add_representer(type(None), lambda s, _: s.represent_scalar(
    'tag:yaml.org,2002:null', ''))
_BUJO_PATH = os.path.join(os.path.expanduser('~'), '.bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.argument('bujo', type=str, required=False)
@click.pass_context
def cli(ctx, bujo=None):
    if bujo:
        action_menu(bujo)
        exit()
    elif ctx.invoked_subcommand is None:
        select_menu()


def action_menu(bujo):
    data = _yaml_r() or {}

    # Set title 
    title = "Bujo: [{}]\n\n(a)dd, (r)emove, (e)dit, (q)uit, (h)elp, (b)ack".format(bujo.upper())
    options = data[bujo.upper()]

    # Create new picker
    picker = Picker(options, title)

    # Set commands
    if picker:
        picker.register_custom_handler(ord('q'), _quit)
        picker.register_custom_handler(ord('a'), _add)
        picker.register_custom_handler(ord('r'), _remove)
        picker.register_custom_handler(ord('e'), _edit)
        picker.register_custom_handler(ord('q'), _quit)
        picker.register_custom_handler(ord('h'), _help)
        picker.register_custom_handler(ord('b'), _back)

        # Start
        option, index = picker.start()

def select_menu():
    data = _yaml_r() or {}

    # Set title and bujo's as options
    title = "Select a Bujo to work / (a)dd a new one / (q)uit / (h)elp"
    options = list(data.keys())

    # Create picker 
    picker = Picker(options, title)

    # Register commands for screen
    picker.register_custom_handler(ord('q'), _quit)
    picker.register_custom_handler(ord('a'), _add_bujo)
    picker.register_custom_handler(ord('h'), _help)

    # Start and head to action menu with choice
    option, index = picker.start()
    action_menu(option)


def take_input(picker, text="", title=""):
    # Input screen setup
    stdscr = curses.initscr()
    stdscr.addstr(0, 0, title)
    editwin = curses.newwin(5,30, 2,1)
    editwin.addstr(text)
    rectangle(stdscr, 1,0, 1+5+1, 1+30+1)
    stdscr.refresh()

    # Get the note
    box = Textbox(editwin)
    box.edit()

    # Return the note
    text = box.gather()
    return str(text).strip()


def _back(picker):
    select_menu()
    pass

def _add(picker):
    # Clear pick screen
    old_title, old_options = picker.title, picker.options
    picker.title, picker.options = "", ""
    picker.draw()

    # Get note to add
    message = take_input(picker, title="Enter new note: (Ctrl+G) to save")

    # Redraw pick screen
    old_options.append(message)
    picker.title, picker.options = old_title, old_options
    picker.draw()

    # Fetch the bujo title
    title_match = re.search(r"\[(.*)\]", picker.title)
    bujo = title_match.group(1)

    # Add to _BUJO_PATH
    data = _yaml_r() or {}
    bujo_values = data[bujo]
    bujo_values.append(message)
    data[bujo] = bujo_values


    # Write to _BUJO_PATH
    _yaml_w(data)

def _add_bujo(picker):
    old_title, old_options = picker.title, picker.options
    picker.title, picker.options = "", ""
    picker.draw()

    bujo = take_input(picker, title="Enter name of new bujo (Ctrl+G) to save")

    old_options.append(bujo.upper())
    picker.title, picker.options = old_title, old_options
    picker.draw()

    data = _yaml_r() or {}
    data[bujo.upper()] = ["Default note, you can delete me by hovering and hitting (r)!"]
    _yaml_w(data)

def _remove(picker):
    data = _yaml_r() or {}

    # Get bujo
    title_match = re.search(r"\[(.*)\]", picker.title)
    bujo = title_match.group(1)

    # Remove value at index
    bujo_values = data[bujo]
    try:
        bujo_values.pop(picker.index)
        picker.options.pop(picker.index)
        if len(picker.options) < 1:
            exit()
    except IndexError:
        _error("No more notes in that bujo")
    data[bujo] = bujo_values

    # Redraw picker
    picker.move_up()
    picker.draw()

    _yaml_w(data)

def _edit(picker):
    title_match = re.search(r"\[(.*)\]", picker.title)
    bujo = title_match.group(1)

    old_title, old_options = picker.title, picker.options
    picker.title, picker.options = "", ""
    picker.draw()

    data = _yaml_r() or {}

    bujo_values = data[bujo]
    note = bujo_values[picker.index]

    edited = take_input(picker, text=note, title="Edit your note (Ctrl+G) to save")

    old_options[picker.index] = edited
    picker.title, picker.options = old_title, old_options
    picker.draw()

    bujo_values[picker.index] = edited

    data[bujo] = bujo_values
    _yaml_w(data)


def _quit(picker):
    return exit()

def _help(picker):
    if "Documentation" in picker.title:
        pass
    else:
        picker.title += "\n\n Documentation can be found at:"
        picker.draw()

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