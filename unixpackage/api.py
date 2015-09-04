from subprocess import call, PIPE
from sys import stdout
from os import path
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


DISTROS = {
    "ubuntu": {
        "base": "basedeb",
        "install": "sudo apt-get install",
        "check": ["dpkg", "--status", ],
    },
    "debian": {
        "base": "basedeb",
        "install": "sudo apt-get install",
        "check": ["dpkg", "--status", ],
    },
    "centos": {
        "base": "baserpm",
        "install": "sudo yum install",
        "check": ["dpkg", "--status", ],
    },
    "redhat": {
        "base": "baserpm",
        "install": "sudo yum install",
        "check": ["rpm", "-q", ],
    },
    "fedora": {
        "base": "baserpm",
        "install": "sudo yum install",
        "check": ["rpm", "-q", ],
    },
    "arch": {
        "base": "arch",
        "install": "sudo pacman -S",
        "check": ["pacman", "-Qs", ],
    },
    "macosbrew": {
        "base": "macosbrew",
        "install": "brew install",
        "check": ["brew", "list", "--versions", ],
    }
}


def return_code_zero(command):
    """Returns True if command called has return code zero."""
    return call(command, stdout=PIPE, stderr=PIPE) == 0


def what_distro_am_i():
    """Return an identifying name for the distro/platform."""
    if sys.platform == "darwin":
        return "macosbrew"
    elif sys.platform == "linux" or sys.platform == "linux2":
        this_distro = platform.linux_distribution()[0].lower()
        if this_distro in DISTROS:
            return this_distro
        else:
            raise UnsupportedPlatform(
                "Linux distro {} is not a supported platform".format(
                    this_distro
                )
            )
    else:
        raise UnsupportedPlatform(
            "Platform '{}' is not currently supported".format(sys.platform)
        )


def package_list(generic_package_list):
    """Get specific packages from generic package."""
    my_distro = what_distro_am_i()
    distro_specific_packages = []
    my_parent = DISTROS[my_distro]["base"]
    cache_dir = path.join(path.expanduser("~"), ".unixpackage")

    if not path.exists(cache_dir):
        os.makedirs(cache_dir)

    for package in generic_package_list:
        cache_filename = path.join(cache_dir, "{}.json".format(package))
        if path.exists(cache_filename):
            with open(cache_filename, 'r') as cache_read_handle:
                package_equivalents = json.loads(cache_read_handle.read())
        else:
            req = requests.get(
                "https://unixpackage.github.io/{}.json".format(package)
            )
            if req.status_code == 200:
                package_equivalents = req.json()

                with open(cache_filename, 'w') as cache_write_handle:
                    cache_write_handle.write(json.dumps(package_equivalents))
            elif req.status_code == 404:
                raise PackageNotFound(
                    ("Package {0} not found at "
                     "https://unixpackage.github.io/{0}.json").format(package)
                )
            else:
                raise NetworkError(
                    ("Error querying https://unixpackage.github.io/{}.json"
                     "- got status code {}.").format(package, req.status_code)
                )

        if my_distro in package_equivalents:
            equivalent = package_equivalents[my_distro]
        elif my_parent in package_equivalents:
            equivalent = package_equivalents[my_parent]
        else:
            raise PackageNotFoundInEquivalents(
                ("Package {0} for distro {1} not found in "
                 "https://unixpackage.github.io/{0}.json").format(
                    package,
                    my_distro
                )
            )

        if type(equivalent) is list:
            distro_specific_packages.extend(equivalent)
        else:
            distro_specific_packages.append(equivalent)

    return distro_specific_packages


def install_command(generic_package_list):
    """Get the install command from a list of packages."""
    my_distro = what_distro_am_i()
    return "{} {}".format(
        DISTROS[my_distro]["install"], " ".join(
            package_list(generic_package_list)
        )
    )


def packages_installed(packages):
    """Verify that the list of packages is installed."""
    if len(packages) > 10:
        packages_installed(packages[10:])
        packages = packages[:10]
    return return_code_zero(
        DISTROS[what_distro_am_i()]["check"] + package_list(packages)
    )


def install(packages):
    """Attempt installation of specified packages (if not installed)."""
    if len(packages) > 10:
        install(packages[10:])
        packages = packages[:10]
    if not packages_installed(packages):
        stdout.write("I need to use sudo to run the following command:\n")
        stdout.write("  ==> {}\n".format(install_command(packages)))
        stdout.flush()
        os.system(install_command(packages))
    else:
        stdout.write(
            "Already installed: {}\n".format(', '.join(packages))
        )
        stdout.flush()
