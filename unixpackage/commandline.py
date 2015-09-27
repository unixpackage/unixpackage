"""UnixPackage command line interface"""
from unixpackage.click import command, group, argument, option, echo
from unixpackage import api, exceptions
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
@option(
    '-r', '--requirements',
    help='Install requirements from given requirements file.'
)
def install(packages, polite, requirements):
    """Install package."""
    try:
        packages = list(packages)
        packages.extend(api.parse_requirements_file(requirements))
        api.install(packages, polite=polite)
    except exceptions.UnixPackageException as error:
        echo(error)
        exit(1)


@command()
@argument('packages', nargs=-1)
@option(
    '-r', '--requirements',
    help='Check if requirements from file are installed.'
)
def check(packages, requirements):
    """Check to see if a package is installed."""
    try:
        packages = list(packages)
        packages.extend(api.parse_requirements_file(requirements))
        if api.packages_installed(packages):
            echo("Package(s) installed")
        else:
            for package in packages:
                if not api.packages_installed([package, ]):
                    echo("Package '{0}' is not installed. Install with 'unixpackage install {0}'".format(
                        package
                    ))
    except exceptions.UnixPackageException as error:
        echo(error)
        exit(1)


@command()
@argument('packages', nargs=-1)
@option(
    '-r', '--requirements',
    help='Show install command for requirements listed in file.'
)
def show(packages, requirements):
    """Display command used to install packages."""
    try:
        packages = list(packages)
        packages.extend(api.parse_requirements_file(requirements))
        echo(api.install_command(packages))
    except exceptions.UnixPackageException as error:
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
