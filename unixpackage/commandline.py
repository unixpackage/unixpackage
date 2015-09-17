"""UnixPackage command line interface"""
from click import command, group, argument, option, echo
from unixpackage import api
from sys import exit
from os import path
import signal
import shutil


@group()
def cli():
    pass


@command()
@argument('packages', nargs=-1)
@option(
    '-p', '--polite', is_flag=True,
    help='Ask politely to install via sudo and double check afterwards.'
)
def install(packages, polite):
    """Install package."""
    try:
        api.install(list(packages), polite=polite)
    except api.UnixPackageException as error:
        echo(error)
        exit(1)


@command()
@argument('packages', nargs=-1)
def check(packages):
    """Check to see if a package is installed."""
    try:
        if api.packages_installed(list(packages)):
            echo("Installed")
        else:
            echo("One of the packages '{}' is missing.".format(
                ','.join(packages)
            ))
    except api.UnixPackageException as error:
        echo(error)
        exit(1)


@command()
@argument('packages', nargs=-1)
def show(packages):
    """Display command used to install packages."""
    try:
        echo(api.install_command(list(packages)))
    except api.UnixPackageException as error:
        echo(error)
        exit(1)


@command()
def cleancache():
    """Clean out package list cache (~/.unixpackage)"""
    shutil.rmtree(
        path.join(path.expanduser("~"), ".unixpackage"), ignore_errors=True
    )


def run():
    """Run UnixPackage CLI"""
    def stop_everything(sig, frame):
        """Exit unixpackage."""
        exit(1)

    signal.signal(signal.SIGINT, stop_everything)
    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGHUP, stop_everything)
    signal.signal(signal.SIGQUIT, stop_everything)
    cli.add_command(install)
    cli.add_command(check)
    cli.add_command(show)
    cli.add_command(cleancache)
    cli()

if __name__ == '__main__':
    run()
