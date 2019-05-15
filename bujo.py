import click
import getpass
from pyfiglet import Figlet
import os.path
import yaml


_BUJO_PATH = os.path.join(os.path.expanduser('~'), 'bujo.yaml')


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-p', '--pager', is_flag=True)
def cli(ctx, pager):
    if ctx.invoked_subcommand is None:
        if pager:
            show_bujo(pager=True)
        else:
            show_bujo()


def show_bujo(pager=False):
    """
    Displays the bujo

    :param pager: Whether to show bujo as a pager
    :type pager: boolean
    :return:
    """
    data = _yaml_r() or {}
    bujos = sorted([bujo for bujo in data])

    output = []

    if data:
        for bujo in bujos:
            output.append(click.style(bujo, reverse=True))
            for index, item in enumerate(data[bujo], start=1):
                output.append(' '*3 + str(index) + ': ' + item)
            else:
                if pager:
                    click.echo_via_pager('\n'.join(output))
                else:
                    for line in output:
                        click.echo(line)
    else:
        click.echo("You don't have any notes saved!")


@cli.command()
@click.option('--custom', '-c', default=False)
def fig(custom):
    """Prints PyBujo or a cool message"""
    f = Figlet(font='slant')
    if custom:
        print(f.renderText(custom))
    else:
        print(f.renderText(getpass.getuser()))


@cli.command()
@click.argument('note', type=str)
@click.option('-b', '--bujo')
def add(note, bujo=None):
    """
    Adds a note to the corresponding bujo
    :param note: The note to add
    :param bujo: The journal to add it to
    :return:
    """
    data = _yaml_r() or {}
    if bujo is None:
        bujo = 'General'

    try:
        if note not in data[bujo]:
            data[bujo].append(note)
        else:
            click.echo("You've already made this note")
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
    try:
        del data[bujo][index-1]
    except (KeyError, IndexError, TypeError):
        click.echo('There is no note {} {}'.format(bujo, index))
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