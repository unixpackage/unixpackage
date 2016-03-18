from unixpackage.package_group import package_group_for_my_distro
from unixpackage.utils import log, warn, check_call
from unixpackage import exceptions
import signal
import os
import time


def parse_requirements_file(filename):
    """Parse Requirements file and return a list of packages."""
    if filename is not None:
        filename = os.path.abspath(filename)
        try:
            with open(filename, "r") as req_file_handle:
                list_of_requirements = [
                    line for line in req_file_handle.read().split('\n') \
                        if line.strip() != "" and not line.startswith("#")
                ]
            return list_of_requirements
        except IOError:
            raise exceptions.RequirementsFileCannotBeRead(filename)
    else:
        return []


def install_command(generic_packages):
    """Return an install command for this distro."""
    if len(generic_packages) == 0:
        raise exceptions.NoPackagesSpecified()
    return package_group_for_my_distro()(generic_packages).install_cmd()


def packages_installed(generic_packages):
    """Verify that the list of packages is installed."""
    if len(generic_packages) == 0:
        raise exceptions.NoPackagesSpecified()
    if len(generic_packages) > 10:
        packages_installed(generic_packages[10:])
        generic_packages = generic_packages[:10]
    return package_group_for_my_distro()(generic_packages).check()


def install(generic_packages, polite=False):
    """Attempt installation of specified packages (if not already installed)."""
    if len(generic_packages) == 0:
        raise exceptions.NoPackagesSpecified()
    if len(generic_packages) > 10:
        install(generic_packages[10:], polite=polite)
        generic_packages = generic_packages[:10]

    package_group = package_group_for_my_distro()(generic_packages)

    if not package_group.check():
        not_preinstalled = package_group.not_installed()
        install_cmd = not_preinstalled.install_cmd()
        if package_group.need_sudo and polite:
            previous_signal = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            log((
                "The following command must be run to continue. I am attempting to run it now:"
                "\n\n\n       {0}\n\n\n"
                "You can also run this command in another window "
                "and then hit Ctrl-C to continue.\n\n"
            ).format(install_cmd))
        try:
            check_call(install_cmd, shell=True)
        except exceptions.CalledProcessError:
            warn("\nWARNING : Command '{0}' returned error code\n\n".format(install_cmd))
        if package_group.need_sudo and polite:
            signal.signal(signal.SIGINT, previous_signal)

        # Double check that the packages were correctly installed
        not_installed_after_install_cmd = not_preinstalled.not_installed()

        if not not_installed_after_install_cmd.empty():
            # Throw meaningful error with the command to re-run to install packages
            raise exceptions.PackageInstallationFailed(
                not_installed_after_install_cmd.generic_package_list,
                not_installed_after_install_cmd.install_cmd()
            )
        else:
            log("Post-install package check for {0} successful!\n".format(
                ", ".join(not_preinstalled.generic_package_list)
            ))
    else:
        log("Already installed: {0}\n".format(', '.join(generic_packages)))
