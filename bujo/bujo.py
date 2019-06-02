import click
import re
import os
import yaml
from curses.textpad import Textbox, rectangle
import curses
from pprint import pprint as pp
from pick import Picker

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
        select_bujo()


def action_menu(bujo):
    data = _yaml_r() or {}

    title = "Bujo: [{}]\n\n(a)dd, (r)emove, (e)dit, (q)uit, (h)elp, (b)ack".format(bujo.upper())
    options = data[bujo.upper()]

    if options and len(options) >= 1:
        picker = Picker(options, title)
    else:
        picker = Picker([""], title)

    picker.register_custom_handler(ord('q'), _quit)
    picker.register_custom_handler(ord('a'), _add)
    picker.register_custom_handler(ord('r'), _remove)
    picker.register_custom_handler(ord('e'), _edit)
    picker.register_custom_handler(ord('q'), _quit)
    picker.register_custom_handler(ord('h'), _help)
    picker.register_custom_handler(ord('b'), _back)
    picker.register_custom_handler(ord('m'), _move)

    option, index = picker.start()


# TODO - Take user to take_input if bujo has no notes
def select_bujo(picker=""):
    data = _yaml_r() or {}

    title = "Select Bujo: / (a)dd a new one / (r)emove bujo and it's notes / (q)uit / (h)elp"
    options = list(data.keys())

    if len(options) >= 1:
        picker = Picker(options, title)
    else:
        options = ["MY FIRST BUJO"]
        data = _yaml_r() or {}
        data["MY FIRST BUJO"]= [""]
        _yaml_w(data)
        picker = Picker(options, title)

    picker.register_custom_handler(ord('q'), _quit)
    picker.register_custom_handler(ord('a'), _add_bujo)
    picker.register_custom_handler(ord('r'), _remove_bujo)
    picker.register_custom_handler(ord('e'), _edit_bujo)
    picker.register_custom_handler(ord('h'), _help)

    option, index = picker.start()
    action_menu(option)


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


def take_input(picker, text="", title=""):
    try:
        columns, rows = os.get_terminal_size(0)
    except OSError:
        columns, rows = os.get_terminal_size(1)
    columns = int(columns)

    # Input screen setup
    stdscr = curses.initscr()
    stdscr.addstr(0, 0, title)
    editwin = curses.newwin(1,columns-2,2,1)
    rectangle(stdscr, 1,0, 1+1+1, 1+columns-2)
    editwin.addstr(text)
    stdscr.refresh()

    # Get the note
    box = Textbox(editwin)
    box.stripspaces = True
    box.edit()

    # Return the note
    text = box.gather()
    text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])
    return str(text).strip()


def _quit(picker):
    return exit()


def _edit_bujo(picker):
    pass


def _move(picker):
    pass


def _add(picker):
    bujo = _get_bujo(picker)
    o_title, o_options = _hide_picker(picker)

    message = take_input(picker, title="Enter new note: (Ctrl+G / ENTER) to save, leave empty to exit")

    if message is "" or message in o_options:
        action_menu(bujo)
        return

    o_options.append(message)
    if o_options[0] is "":
        del o_options[0]
    _show_picker(picker, o_title, o_options)

    data = _yaml_r() or {}
    bujo_values = data[bujo]
    bujo_values.append(message)
    data[bujo] = bujo_values

    _yaml_w(data)


def _add_bujo(picker):
    o_title, o_options = _hide_picker(picker)
    message = take_input(picker, title="Enter new Bujo name: (Ctrl+G / ENTER) to save, leave empty to exit")
    if message is "" or message.upper() in o_options:
        select_bujo()
        return
    o_options.append(message.upper())
    _show_picker(picker, o_title, o_options)

    data = _yaml_r() or {}
    data[message.upper()] = [""]
    _yaml_w(data)


def _remove(picker):
    bujo = _get_bujo(picker)

    data = _yaml_r() or {}
    bujo_values = data[bujo]
    try:
        bujo_values.pop(picker.index)
        picker.options.pop(picker.index)
        if len(picker.options) < 1:
            _back(picker)
    except IndexError:
        _quit()
    data[bujo] = bujo_values

    picker.move_up()
    picker.draw()

    _yaml_w(data)


def _remove_bujo(picker):
    bujo = picker.options[picker.index]

    data = _yaml_r() or {}
    try:
        data.pop(bujo, None)
        picker.options.pop(picker.index)
        if len(picker.options) < 1:
            _back(picker)
    except IndexError:
        _back(picker)

    picker.move_up()
    picker.draw()

    _yaml_w(data)


def _edit(picker):
    bujo = _get_bujo(picker)

    o_title, o_options = _hide_picker(picker)
    data = _yaml_r() or {}

    bujo_values = data[bujo]
    note = bujo_values[picker.index]

    edited = take_input(picker, text=note, title="Edit your note (Ctrl+G) to save")

    o_options[picker.index] = edited
    _show_picker(picker, o_title, o_options)

    bujo_values[picker.index] = edited
    data[bujo] = bujo_values
    _yaml_w(data)


def _help(picker):
    if "Documentation" in picker.title:
        pass
    else:
        picker.title += "\n\nDocumentation can be found at:"
        picker.draw()
    pass


def _set_title(picker, title):
    picker.title = title
    picker.draw()


def _set_options(picker, options):
    picker.options = options
    picker.draw()

def _hide_picker(picker):
    old_title, old_options = picker.title, picker.options

    picker.title, picker.options = "", ""
    picker.draw()
    return (old_title, old_options)

def _show_picker(picker, title, options):
    picker.title, picker.options = title, options
    picker.draw()


def _get_bujo(picker):
    title_match = re.search(r"\[(.*)\]", picker.title)
    return title_match.group(1)


def _back(picker):
    select_bujo()


if __name__ == '__main__':
    cli = click.CommandCollection(sources=[cli])
    cli()
