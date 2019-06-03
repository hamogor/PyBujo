#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bujo
# Copyright (c) 2019 Harry Morgan <ferovax@gmail.com>
# A CLI tool for tracking things simply

__version__ = "0.2"
__author__ = "Harry Morgan <ferovax@gmail.com>"
__copyright__ = "Copyright (c) 2019 Harry Morgan <ferovax@gmail.com>"
__all__ = ['EditBox', 'cli']

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


@click.group(invoke_without_command=True, context_settings=_CONTEXT_SETTINGS)
@click.argument('bujo', type=str, required=False)
@click.pass_context
def cli(ctx, bujo=None):
    if bujo:
        action_menu(bujo)
    elif ctx.invoked_subcommand is None:
        select_bujo()


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
        editwin = curses.newwin(1,columns-2,21)
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


    def add(self):
        pass


    def remove_bujo(self):
        pass


    def edit_bujo(self):
        pass


    def help_link(self):
        pass


    def quit(self):
        return exit()


    def add(self):
        pass


    def remove(self):
        pass


    def edit(self):
        pass


    def back(self):
        pass



    def move(self):
        pass


    def set_commands(self, menu_type):
       if self.type_ is "select":
           self.register_custom_handler(ord('q'), self.quit)
           self.register_custom_handler(ord('a'), self.add)
           self.register_custom_handler(ord('r'), self.remove_bujo)
           self.register_custom_handler(ord('e'), self.edit_bujo)
           self.register_custom_handler(ord('h'), self.help_link)
       elif self.type_ is "bujo":
           self.register_custom_handler(ord('q'), self.quit)
           self.register_custom_handler(ord('a'), self.add)
           self.register_custom_handler(ord('r'), self.remove)
           self.register_custom_handler(ord('e'), self.edit)
           self.register_custom_handler(ord('q'), self.quit)
           self.register_custom_handler(ord('h'), self.help_link)
           self.register_custom_handler(ord('b'), self.back)
           self.register_custom_handler(ord('m'), self.move)


    def __init__(self, title, options, type_):
        self.title = title
        self.options = options
        self.type_ = type_
        self.custom_handlers = {}

        if len(options) < 1:
            self.options = ["MY FIRST BUJO"]
            data = _yaml_r() or {}
            data["MY FIRST BUJO"] = [""]

        self.set_commands("select")





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
