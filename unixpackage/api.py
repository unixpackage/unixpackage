from unixpackage.package_group import package_group_for_my_distro
from unixpackage.utils import log, warn, check_call
from unixpackage import exceptions
import signal


def install_command(generic_packages):
    """Return an install command for this distro."""
    return package_group_for_my_distro()(generic_packages).install_cmd()


def packages_installed(generic_packages):
    """Verify that the list of packages is installed."""
    if len(generic_packages) > 10:
        packages_installed(generic_packages[10:])
        generic_packages = generic_packages[:10]
    return package_group_for_my_distro()(generic_packages).check()


def install(generic_packages, polite=False):
    """Attempt installation of specified packages (if not already installed)."""
    if len(generic_packages) > 10:
        install(generic_packages[10:])
        generic_packages = generic_packages[:10]

    package_group = package_group_for_my_distro()(generic_packages)

    if not package_group.check():
        install_cmd = package_group.install_cmd()
        if package_group.need_sudo and polite:
            ctrl_c_message = ("You can also run this command in another window"
                              "and then hit Ctrl-C to continue.\n\n") \
                              if signal.getsignal(signal.SIGINT) == signal.SIG_IGN else ""

            log((
                "The following command must be run to continue. I am attempting to run it now:"
                "\n\n\n       {0}\n\n\n"
                "{1}"
            ).format(install_cmd, ctrl_c_message))
        try:
            check_call(install_cmd, shell=True)
        except exceptions.CalledProcessError:
            warn("\nWARNING : Command '{0}' returned error code\n\n".format(install_cmd))

        # Double check that the packages were correctly installed
        if not package_group.check():
            not_yet_installed = []
            for package in generic_packages:
                package_group_of_one = package_group_for_my_distro()([package])

                if not package_group_of_one.check():
                    not_yet_installed.append(package)

            # Throw meaningful error with the command to re-run to install packages
            not_yet_installed_package_group = package_group_for_my_distro()(not_yet_installed)
            if len(not_yet_installed) > 0:
                raise exceptions.PackageInstallationFailed(
                    not_yet_installed,
                    not_yet_installed_package_group.install_cmd()
                )
    else:
        log("Already installed: {0}\n".format(', '.join(generic_packages)))
