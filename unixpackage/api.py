from subprocess import call, PIPE
from sys import stdout, stderr
from os import path
import subprocess
import requests
import platform
import json
import sys
import os


class UnixPackageException(Exception):
    pass


class PackageNotFoundInEquivalents(UnixPackageException):
    pass


class UnsupportedPlatform(UnixPackageException):
    pass


class PackageNotFound(UnixPackageException):
    pass


class NetworkError(UnixPackageException):
    pass


class PackageDescriptionNotUnderstood(UnixPackageException):
    pass


class PackageInstallationFailed(UnixPackageException):
    pass


class ConnectionFailure(UnixPackageException):
    pass


DISTROS = {
    "ubuntu": {
        "base": "basedeb",
        "install": "apt-get install",
        "sudoinstall": True,
        "check": ["dpkg", "--status", ],
    },
    "debian": {
        "base": "basedeb",
        "install": "apt-get install",
        "sudoinstall": True,
        "check": ["dpkg", "--status", ],
    },
    "centos": {
        "base": "baserpm",
        "install": "yum install",
        "sudoinstall": True,
        "check": ["dpkg", "--status", ],
    },
    "redhat": {
        "base": "baserpm",
        "install": "yum install",
        "sudoinstall": True,
        "check": ["rpm", "-q", ],
    },
    "fedora": {
        "base": "baserpm",
        "install": "yum install",
        "sudoinstall": True,
        "check": ["rpm", "-q", ],
    },
    "arch": {
        "base": "arch",
        "install": "pacman -S",
        "sudoinstall": True,
        "check": ["pacman", "-Q", ],
    },
    "macosbrew": {
        "base": "macosbrew",
        "install": "brew install",
        "sudoinstall": False,
        "check": ["brew", "list", "--versions", ],
    }
}


def return_code_zero(command):
    """Returns True if command called has return code zero."""
    return call(command, stdout=PIPE, stderr=PIPE) == 0


def is_string(obj):
    """Is the object a string/unicode?"""
    return str(type(obj)) == "<type 'unicode'>" or str(type(obj)) == "<class 'str'>"


def what_distro_am_i():
    """Return an identifying name for the distro/platform."""
    if sys.platform == "darwin":
        return "macosbrew"
    elif sys.platform == "linux" or sys.platform == "linux2":
        this_distro = platform.linux_distribution()[0].lower()
        if this_distro in DISTROS:
            return this_distro
        else:
            raise UnsupportedPlatform((
                "Linux distro {0} is not supported yet.\n"
                "Raise an issue at http://github.com/unixpackage/unixpackage"
                " for help."
            ).format(this_distro))
    else:
        raise UnsupportedPlatform(
            "Platform '{0}' is not currently supported".format(sys.platform)
        )


def need_sudo_for_install():
    return DISTROS[what_distro_am_i()]['sudoinstall']


def package_list(generic_package_list):
    """Get specific packages from generic package."""
    my_distro = what_distro_am_i()
    distro_specific_packages = []
    my_parent = DISTROS[my_distro]["base"]
    cache_dir = path.join(path.expanduser("~"), ".unixpackage")

    if not path.exists(cache_dir):
        os.makedirs(cache_dir)

    for package in generic_package_list:
        cache_filename = path.join(cache_dir, "{0}.json".format(package))
        if path.exists(cache_filename):
            with open(cache_filename, 'r') as cache_read_handle:
                package_equivalents = json.loads(cache_read_handle.read())
        else:
            stdout.write((
                "Requesting and caching correct package names for: {0}...\n"
            ).format(package))
            stdout.flush()

            try:
                req = requests.get(
                    "https://unixpackage.github.io/{0}.json".format(package)
                )
            except requests.exceptions.ConnectionError:
                raise ConnectionFailure((
                    "Failure when connecting to https://unixpackage.github.io/{0}.json. "
                    "Is your internet working?"
                ).format(package))

            if req.status_code == 200:
                package_equivalents = req.json()

                with open(cache_filename, 'w') as cache_write_handle:
                    cache_write_handle.write(json.dumps(package_equivalents))
            elif req.status_code == 404:
                raise PackageNotFound((
                    "Package {0} not found at "
                    "https://unixpackage.github.io/{0}.json\n"
                    "Please consider adding it if it should exist!\n"
                    "Simply raise an issue or issue a pull request on: "
                    "http://github.com/unixpackage/unixpackage.github.io"
                ).format(package))
            else:
                raise NetworkError((
                    "Error querying https://unixpackage.github.io/{0}.json"
                    "- got status code {1}."
                ).format(package, req.status_code))

        if my_distro in package_equivalents:
            equivalent = package_equivalents[my_distro]
        elif my_parent in package_equivalents:
            equivalent = package_equivalents[my_parent]
        else:
            raise PackageNotFoundInEquivalents((
                "Package {0} for distro {1} not found in "
                "https://unixpackage.github.io/{0}.json // ~/.unixpackage/{0}.json"
            ).format(package, my_distro))

        if type(equivalent) is list:
            distro_specific_packages.extend(equivalent)
        elif is_string(equivalent):
            distro_specific_packages.append(equivalent)
        elif equivalent is None:
            pass
        else:
            raise PackageDescriptionNotUnderstood((
                "Format of {0} equivalent for package "
                "{1} was not understood."
            ).format(my_distro, package))

    return distro_specific_packages


def install_command(generic_package_list):
    """Get the install command from a list of packages."""
    my_distro = what_distro_am_i()
    return "{0}{1} {2}".format(
        "sudo " if need_sudo_for_install() else "",
        DISTROS[my_distro]["install"],
        " ".join(package_list(generic_package_list)),
    )


def packages_installed(packages):
    """Verify that the list of packages is installed."""
    if len(packages) > 10:
        packages_installed(packages[10:])
        packages = packages[:10]
    return return_code_zero(
        DISTROS[what_distro_am_i()]["check"] + package_list(packages)
    )


def install(packages, polite=False):
    """Attempt installation of specified packages (if not installed)."""
    if len(packages) > 10:
        install(packages[10:])
        packages = packages[:10]
    if not packages_installed(packages):
        if need_sudo_for_install() and polite:
            stdout.write((
                "The following command must be run to continue:\n"
                "  ==> {0}\n"
                "If you like, you can copy and paste the command "
                "and run it in another terminal window.\n"
                "After attempting to run the command "
                "unixpackage will verify successful installation.\n"
            ).format(install_command(packages)))
            stdout.flush()
        os.system(install_command(packages))
        try:
            subprocess.check_call("exit 1", shell=True)
        except subprocess.CalledProcessError:
            stderr.write(
                "\nWARNING : Command failed '{0}'\n\n".format(install_command(packages))
            )
        if not packages_installed(packages):
            raise PackageInstallationFailed(
                "Package installation of {0} failed.".format(', '.join(packages))
            )
    else:
        stdout.write(
            "Already installed: {0}\n".format(', '.join(packages))
        )
        stdout.flush()
