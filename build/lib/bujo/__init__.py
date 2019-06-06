#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bujo
# Copyright (c) 2019 Harry Morgan <ferovax@gmail.com>
# A CLI tool for tracking things simply

__version__ = "0.2"
__author__ = "Harry Morgan <ferovax@gmail.com>"
__copyright__ = "Copyright (c) 2019 Harry Morgan <ferovax@gmail.com>"
__all__ = ['Bujo', 'cli']

import click
import re
import os
import yaml
from curses.textpad import Textbox, rectangle
import curses
from pprint import pprint as pp
from pick import Picker


yaml.add_representer(type(None), lambda s, _: s.represent_scalar(
    'tag:yaml.org,2002,null', ''))
_BUJO_PATH = os.path.join(os.path.expanduser('~'), '.bujo.yaml')
_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

# TODO - Handle empty values and no bujos gracefully


@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.argument('journal', type=str, required=False)
@click.pass_context
def cli(ctx, journal=None):
    if journal:
        init_action_menu(journal)
    elif ctx.invoked_subcommand is None:
        init_select_menu()


def init_action_menu(journal=None):
    data = _yaml_r() or {}
    if journal.upper() in data.keys():
        title = "Bujo [{}]\n\n\n(a)dd, (r)emove, (e)dit, (m)ove, (q)uit, (h)elp, (b)ack".format(journal.upper())
        options = data[journal.upper()]
        type_ = "bujo"
        action_menu = Bujo(title, options, type_, journal=journal.upper())
        action_menu.start()
    else:
        click.echo(click.style("No bujo named '{}'".format(journal.upper()), fg='red'))


def init_select_menu():
    data = _yaml_r() or {}

    title = "Select Bujo (ENTER): (a)dd, (e)dit, (r)emove, (q)uit, (h)elp\n\n\n"
    options = list(data.keys())
    type_ = "select"

    select_menu = Bujo(title, options, type_)
    selected = select_menu.options[select_menu.index]
    init_action_menu(selected)

def init_move_menu(note):
    data = _yaml_r() or {}
    title = "Which bujo do you want to move {} to?".format(note)
    options = list(data.keys())
    type_ = "select"

    move_menu = Bujo(title, options, type_)
    selected = move_menu.options[move_menu.index]
    return selected

class EditBox(object):

    def __init__(self, title, text, box):
        self.title = title
        self.text = text
        self.box = box

        try:
            columns, rows = os.get_terminal_size(0)
        except OSError:
            columns, rows = os.get_terminal_size(1)
        columns = int(columns)

        stdscr = curses.initscr()
        stdscr.addstr(0,0,self.title)
        editwin = curses.newwin(1,columns-2,2,1)
        rectangle(stdscr, 1,0, 1+1+1, 1+columns-2)
        editwin.addstr(self.text)
        stdscr.refresh()
        self.box = Textbox(editwin)
        return


    def take_input(self, box):
        box.stripspaces = True
        box.edit()

        text = box.gather()
        text = "".join([s for s in text.splitlines(True) if s.strip("\r\n")])
        return str(text).strip()


class Bujo(Picker):


    def __init__(self, title, options, type_, indicator='>',
                 default_index=0, multi_select=False, min_selection_count=0,
                 options_map_func=None, journal=""):

        if len(options) < 1:
            self.options = ["MY FIRST BUJO"]
            data = _yaml_r() or {}
            data["MY FIRST BUJO"] = [""]
            _yaml_w(data)

        self.title = title
        self.options = options
        self.type_ = type_
        self.custom_handlers = {}
        self.indicator = '>'
        self.default_index = default_index
        self.multi_select = False
        self.min_selection_count=0
        self.options_map_func = None
        self.index = default_index
        self.journal = journal


        self.set_commands(self.type_)

    def set_commands(self, menu_type):
       if self.type_ is "select":
           self.register_custom_handler(ord('q'), self.quit)
           self.register_custom_handler(ord('a'), self.add_bujo)
           self.register_custom_handler(ord('r'), self.remove_bujo)
           self.register_custom_handler(ord('e'), self.edit_bujo)
           self.register_custom_handler(ord('h'), self.help_link)
           return self.start()
       elif self.type_ is "bujo":
           self.register_custom_handler(ord('q'), self.quit)
           self.register_custom_handler(ord('a'), self.add)
           self.register_custom_handler(ord('r'), self.remove)
           self.register_custom_handler(ord('e'), self.edit)
           self.register_custom_handler(ord('h'), self.help_link)
           self.register_custom_handler(ord('b'), self.back)
           self.register_custom_handler(ord('m'), self.move)
           return self.start()


    def add(self, instance):
        edit = EditBox("Add a new note (ENTER to save), leave blank to cancel", "", instance)
        new_note = edit.take_input(edit.box)
        if new_note is "":
            pass
        else:
            data = _yaml_r() or {}
            # Get correct key
            bujo = self.journal
            if bujo in data.keys():
                bujo_values = data[bujo]
                bujo_values.append(new_note)
                data[bujo] = bujo_values
                _yaml_w(data)
            self.options.append(new_note)
            self.draw()


    def add_bujo(self, instance):
        edit = EditBox("Add a new Bujo (ENTER to save), leave blank to cancel", "", instance)
        new_bujo = edit.take_input(edit.box).upper()
        if new_bujo is "":
            pass
        else:
            data = _yaml_r() or {}
            data[new_bujo] = [""]
            _yaml_w(data)
        self.options.append(new_bujo)
        self.draw()


    def remove_bujo(self, instance):
        if len(self.options) < 1:
            pass
        elif len(self.options) >= 1:
            bujo = self.options[self.index]
            self.options.pop(self.index)
            self.move_up()
            self.draw()
            data = _yaml_r() or {}
            try:
                data.pop(bujo, None)
            except IndexError:
                self.index -= 1
            _yaml_w(data)


    def edit_bujo(self, instance):
        if len(self.options) < 1:
            pass
        elif len(self.options) >= 1:
            bujo = self.options[self.index]
            data = _yaml_r() or {}
            bujo_values = data[bujo]

            edit = EditBox("Edit bujo name (ENTER to save), leave blank to cancel", "", instance)
            edited_bujo = edit.take_input(edit.box).upper()
            if edited_bujo is "":
                pass
            else:
                data[edited_bujo] = data.pop(bujo)
                self.options[self.index] = edited_bujo
                self.draw()

                _yaml_w(data)


    def edit(self, instance):
        if len(self.options) < 1:
            pass
        elif len(self.options) >= 1:
            note = self.options[self.index]

            edit = EditBox("Edit note (ENTER to save), leave blank to cancel", "", instance)
            edited_note = edit.take_input(edit.box)
            if edited_note is "":
                pass
            else:
                data = _yaml_r() or {}
                bujo_values = data[self.journal]
                note = bujo_values[self.index]
                self.options[self.index] = edited_note
                bujo_values[self.index] = edited_note
                data[self.journal] = bujo_values

                _yaml_w(data)


    def move(self, instance):
        if len(self.options) < 1:
            pass
        elif len(self.options) >= 1:
            note = self.options[self.index]

            self.options.pop(self.index)
            if len(self.options) < 1:
                self.options.append("")
                self.draw()

            destination = init_move_menu(note)
            data = _yaml_r() or {}


            # Remove from here
            from_values = data[self.journal]
            from_values.pop(self.index)
            data[self.journal] = from_values

            # Add to destination
            to_values = data[destination]
            to_values.append(note)
            data[destination] = to_values

            _yaml_w(data)

            init_action_menu(destination)


    def help_link(self, instance):
        if self.type_ is "select":
            self.title += "Documentation can be found at: https://github.com/oref/PyBujo"
        elif self.type_ is "bujo":
            self.title += "\n\nDocumentation can be found at: https://github.com/oref/PyBujo"

        self.draw()


    def quit(self, instance):
        return exit()


    def remove(self, instance):
        if len(self.options) < 1:
            pass
        elif len(self.options) >= 1:
            self.options.pop(self.index)
            self.move_up()
            self.draw()
            data = _yaml_r() or {}
            bujo_values = data[self.journal]
            bujo_values.pop(self.index)
            data[self.journal] = bujo_values
            _yaml_w(data)


    def back(self, instance):
        init_select_menu()


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
