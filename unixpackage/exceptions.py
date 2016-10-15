
class UnixPackageException(Exception):
    """Base class for all unixpackage exceptions."""
    pass


class RequirementsFileCannotBeRead(UnixPackageException):
    def __init__(self, filename):
        super(RequirementsFileCannotBeRead, self).__init__((
            "Error reading requirements file '{0}'\n"
        ).format(filename))


class PackageNotFoundInEquivalents(UnixPackageException):
    def __init__(self, package_equivalents, distro):
        super(PackageNotFoundInEquivalents, self).__init__((
            "Package for distro {1} not found in {0}\n"
            "Try running 'unixpackage cleancache' or "
            "raise an issue at https://github.com/unixpackage/unixpackage.github.io/"
        ).format(package_equivalents, distro))


class UnsupportedPlatform(UnixPackageException):
    def __init__(self, this_distro):
        super(UnsupportedPlatform, self).__init__((
            "Platform {0} is not supported yet.\n"
            "Raise an issue at http://github.com/unixpackage/unixpackage"
            " for help."
        ).format(this_distro))


class NoPackagesSpecified(UnixPackageException):
    def __init__(self):
        super(NoPackagesSpecified, self).__init__("No packages specified.")


class PackageNotFound(UnixPackageException):
    def __init__(self, generic_package_name, url):
        super(PackageNotFound, self).__init__((
            "Package {0} not found at {1}\n"
            "Please consider adding it if you think it should exist!\n"
            "Simply raise an issue or issue a pull request on: "
            "http://github.com/unixpackage/unixpackage.github.io"
        ).format(generic_package_name, url))


class NetworkError(UnixPackageException):
    def __init__(self, url, error):
        super(NetworkError, self).__init__((
            "Error querying https://unixpackage.github.io/{0}.json"
            "- Reason: {1}."
        ).format(package, error))


class PackageDescriptionNotUnderstood(UnixPackageException):
    def __init__(self, package):
        super(PackageDescriptionNotUnderstood, self).__init__((
            "Problem decoding package {0}. Please raise an issue at "
            "http://github.com/unixpackage/unixpackage.github.io"
        ).format(package))


class PackageInstallationFailed(UnixPackageException):
    def __init__(self, generic_package_names, installation_command):
        super(PackageInstallationFailed, self).__init__((
            "Package installation of {0} failed. Try again with: '{1}'"
        ).format(', '.join(generic_package_names), installation_command))


class ConnectionFailure(UnixPackageException):
    def __init__(self, url):
        super(ConnectionFailure, self).__init__((
                "Failure when connecting to {0}\n"
                "Is your internet working?"
            ).format(url))


class DistroVersionNotFound(UnixPackageException):
    def __init__(self, distro_and_version):
        super(DistroVersionNotFound, self).__init__((
                "Couldn't find distro and version {0}\n"
                "This is a bug! Please raise a ticket at https://github.com/unixpackage/unixpackage"
            ).format(distro_and_version))

class CalledProcessError(UnixPackageException):
    pass
