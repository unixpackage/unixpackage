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
        """Base method to get a specific package (this method must be overridden)."""
        raise exceptions.PackageNotFoundInEquivalents(package_equivalents, self.distro)


class DebPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "apt-get install -y"
    check_cmd = ["dpkg", "--status", ]
    distro = "Debian"

    def get_specific_package(self, package_equivalents):
        if "basedeb" in package_equivalents:
            return package_equivalents["basedeb"]
        return super(DebPackageGroup, self).get_specific_package(package_equivalents)


class DebianPackageGroup(DebPackageGroup):
    def get_specific_package(self, package_equivalents):
        if "debian" in package_equivalents:
            return package_equivalents["debian"]
        return super(DebianPackageGroup, self).get_specific_package(package_equivalents)


class UbuntuPackageGroup(DebPackageGroup):
    distro = "Ubuntu"

    def get_specific_package(self, package_equivalents):
        if "ubuntu" in package_equivalents:
            return package_equivalents["ubuntu"]
        return super(UbuntuPackageGroup, self).get_specific_package(package_equivalents)


class ArchPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "pacman -Sy"
    check_cmd = ["pacman", "-Q", ]
    distro = "Arch"

    def get_specific_package(self, package_equivalents):
        if "arch" in package_equivalents:
            return package_equivalents["arch"]
        return super(ArchPackageGroup, self).get_specific_package(package_equivalents)


class RPMPackageGroup(PackageGroup):
    need_sudo = True
    install_prefix = "yum -y install"
    check_cmd = ["rpm", "-q", ]
    distro = "RPM Distro"

    def get_specific_package(self, package_equivalents):
        if "baserpm" in package_equivalents:
            return package_equivalents["baserpm"]
        return super(RPMPackageGroup, self).get_specific_package(package_equivalents)


class CentOSPackageGroup(RPMPackageGroup):
    distro = "CentOS"

    def get_specific_package(self, package_equivalents):
        if "centos" in package_equivalents:
            return package_equivalents["centos"]
        return super(CentOSPackageGroup, self).get_specific_package(package_equivalents)


class FedoraPackageGroup(RPMPackageGroup):
    distro = "Fedora"

    def get_specific_package(self, package_equivalents):
        if "fedora" in package_equivalents:
            return package_equivalents["fedora"]
        return super(FedoraPackageGroup, self).get_specific_package(package_equivalents)


class RedHatPackageGroup(RPMPackageGroup):
    distro = "Red Hat"

    def get_specific_package(self, package_equivalents):
        if "redhat" in package_equivalents:
            return package_equivalents["redhat"]
        return super(RedHatPackageGroup, self).get_specific_package(package_equivalents)


class MacOSBrewPackageGroup(PackageGroup):
    need_sudo = False
    install_prefix = "brew install"
    distro = "Mac OS X"

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

    def get_specific_package(self, package_equivalents):
        if "macosbrew" in package_equivalents:
            return package_equivalents["macosbrew"]
        return super(MacOSBrewPackageGroup, self).get_specific_package(package_equivalents)


def package_group_for_my_distro():
    """Factory that returns a class representing the distro currently being used."""
    if sys.platform == "darwin":
        return MacOSBrewPackageGroup
    elif sys.platform in ["linux", "linux2", "linux3", ]:
        LINUX_DISTROS = {
            "ubuntu": UbuntuPackageGroup,
            "redhat": RedHatPackageGroup,
            "fedora": FedoraPackageGroup,
            "centos": CentOSPackageGroup,
            "arch": ArchPackageGroup,
            "debian": DebianPackageGroup,
        }

        this_distro = utils.lsb_release().lower()
        if this_distro in LINUX_DISTROS:
            return LINUX_DISTROS[this_distro]
        else:
            raise exceptions.UnsupportedPlatform(this_distro)
    else:
        raise exceptions.UnsupportedPlatform(sys.platform)
