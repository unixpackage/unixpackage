from unixpackage import exceptions
from unixpackage import utils
from sys import stdout
from os import path
import platform
import json
import sys
import os


class PackageGroup(object):
    """Representation of a group of generic packages from generic package names."""
    need_sudo = True

    def __init__(self, generic_package_list):
        """Initialize and download/retrieve from cache distro specific package names."""
        self.generic_package_list = generic_package_list
        self.specific_packages = []

        for package in generic_package_list:
            cache_dir = path.join(path.expanduser("~"), ".unixpackage")
            if not path.exists(cache_dir):
                os.makedirs(cache_dir)

            cache_filename = path.join(cache_dir, "{0}.json".format(package))
            if path.exists(cache_filename):
                package_equivalents = utils.get_json_from_file(cache_filename)
            else:
                utils.log((
                    "Downloading and caching correct package names for: {0}...\n"
                ).format(package))

                url = "https://unixpackage.github.io/{0}.json".format(package)
                contents = utils.get_request(url)

                if contents is None:
                    raise exceptions.PackageNotFound(package, url)
                else:
                    package_equivalents = json.loads(contents)
                    utils.save_json_to_file(cache_filename, package_equivalents)

            specific_package_equivalent = self.get_specific_package(package_equivalents)

            if specific_package_equivalent is not None:
                if type(specific_package_equivalent) is list:
                    self.specific_packages.extend(specific_package_equivalent)
                elif utils.is_string(specific_package_equivalent):
                    self.specific_packages.append(specific_package_equivalent)
                elif specific_package_equivalent is None:
                    pass
                else:
                    raise PackageDescriptionNotUnderstood(package)

    def empty(self):
        """If the generic packages have no equivalent in this distro, this may be true."""
        return len(self.specific_packages) == 0

    def install_cmd(self):
        """Get the distro-specific install command for these packages."""
        return "{0}{1} {2}".format(
            "sudo " if self.need_sudo else "",
            self.install_prefix,
            " ".join(self.specific_packages),
        )

    def check(self):
        """Check if the packages are installed."""
        if self.empty():
            return True
        else:
            return utils.return_code_zero(self.check_cmd + self.specific_packages)

    def not_installed(self):
        """Return a package group of packages not installed from this group."""
        not_installed_list = []
        for package in self.generic_package_list:
            package_group_of_one = package_group_for_my_distro()([package])

            if not package_group_of_one.check():
                not_installed_list.append(package)
        return package_group_for_my_distro()(not_installed_list)

    def get_specific_package(self, package_equivalents):
        """Base method to get a specific package."""
        for x in self.__class__.__mro__[:-2]:
            if x.name in package_equivalents:
                return package_equivalents[x.name]
        raise exceptions.PackageNotFoundInEquivalents(package_equivalents, self.distro)


class DebPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "apt-get install -y"
    check_cmd = ["dpkg", "--status", ]
    distro = "Debian"
    name = "basedeb"


class DebianPackageGroup(DebPackageGroup):
    name = "debian"


class DebianSqueezePackageGroup(DebianPackageGroup):
    name = "debian-squeeze"


class DebianSqueezeLTSPackageGroup(DebianPackageGroup):
    name = "debian-squeeze-lts"


class DebianWheezyPackageGroup(DebianPackageGroup):
    name = "debian-wheezy"


class DebianJessiePackageGroup(DebianPackageGroup):
    name = "debian-jessie"


class DebianStretchPackageGroup(DebianPackageGroup):
    name = "debian-stretch"


class DebianSidPackageGroup(DebianPackageGroup):
    name = "debian-sid"


class UbuntuPackageGroup(DebPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu"


class UbuntuPrecisePackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-precise"


class UbuntuTrustyPackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-trusty"


class UbuntuVividPackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-vivid"


class UbuntuWilyPackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-wily"


class UbuntuXenialPackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-xenial"

class UbuntuYakketyPackageGroup(UbuntuPackageGroup):
    distro = "Ubuntu"
    name = "ubuntu-yakkety"


class ArchPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "pacman -Sy"
    check_cmd = ["pacman", "-Q", ]
    distro = "Arch"
    name = "arch"


class RPMPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "yum -y install"
    check_cmd = ["rpm", "-q", ]
    distro = "RPM Distro"
    name = "baserpm"


class CentOSPackageGroup(RPMPackageGroup):
    distro = "CentOS"
    name = "centos"


class FedoraPackageGroup(RPMPackageGroup):
    distro = "Fedora"
    name = "fedora"


class RedHatPackageGroup(RPMPackageGroup):
    distro = "Red Hat"
    name = "redhat"


class MacOSBrewPackageGroup(PackageGroup):
    need_sudo = False
    install_prefix = "brew install"
    distro = "Mac OS X"
    name = "macosbrew"

    def check(self):
        """brew list --versions will simply not output not-installed packages specified."""
        if not self.empty():
            brew_list_output = utils.check_output(
                ["brew", "list", "--versions", ] + self.specific_packages
            ).decode("utf8").rstrip()
            brew_list_installed_pkgs = [x for x in brew_list_output.split('\n') if x != ""]
            return len(self.specific_packages) == len(brew_list_installed_pkgs)
        else:
            return True


def package_group_for_my_distro():
    """Factory that returns a class representing the distro currently being used."""
    if sys.platform == "darwin":
        return MacOSBrewPackageGroup
    elif sys.platform in ["linux", "linux2", "linux3", ]:
        LINUX_DISTROS = {
            "linuxmint": UbuntuPackageGroup,
            "redhat": RedHatPackageGroup,
            "fedora": FedoraPackageGroup,
            "centos": CentOSPackageGroup,
            "manjarolinux": ArchPackageGroup,
            "arch": ArchPackageGroup,
            "debian-": DebianPackageGroup,
            "debian-squeeze": DebianSqueezePackageGroup,
            "debian-squeeze-lts": DebianSqueezeLTSPackageGroup,
            "debian-wheezy": DebianWheezyPackageGroup,
            "debian-jessie": DebianJessiePackageGroup,
            "debian-stretch": DebianStretchPackageGroup,
            "debian-sid": DebianSidPackageGroup,
            "ubuntu-": UbuntuPackageGroup,
            "ubuntu-precise": UbuntuPrecisePackageGroup,
            "ubuntu-trusty": UbuntuTrustyPackageGroup,
            "ubuntu-vivid": UbuntuVividPackageGroup,
            "ubuntu-wily": UbuntuWilyPackageGroup,
            "ubuntu-xenial": UbuntuXenialPackageGroup,
            "ubuntu-yakkety": UbuntuYakketyPackageGroup,
        }

        this_distro = utils.lsb_release().lower()

        if this_distro in ["debian", "ubuntu",]:
            distro_and_version = "{0}-{1}".format(
                this_distro, utils.lsb_release_codename().lower()
            )
            if distro_and_version not in LINUX_DISTROS.keys():
                raise exceptions.DistroVersionNotFound(distro_and_version)
            return LINUX_DISTROS[distro_and_version]
        else:
            if this_distro in LINUX_DISTROS:
                return LINUX_DISTROS[this_distro]
            else:
                raise exceptions.UnsupportedPlatform(this_distro)
    else:
        raise exceptions.UnsupportedPlatform(sys.platform)
