
class UnixPackageException(Exception):
    """Base class for all unixpackage exceptions."""
    pass


class PackageNotFoundInEquivalents(UnixPackageException):
    def __init__(self, generic_package_name, distro):
        super(PackageNotFoundInEquivalents, self).__init__((
            "Package {0} for distro {1} not found in "
            "https://unixpackage.github.io/{0}.json "
            "or in cache file ~/.unixpackage/{0}.json.\n Try running "
            "unixpackage cleanpkg and try again."
        ).format(generic_package_name, distro))


class UnsupportedPlatform(UnixPackageException):
    def __init__(self, this_distro):
        super(UnsupportedPlatform, self).__init__((
            "Platform {0} is not supported yet.\n"
            "Raise an issue at http://github.com/unixpackage/unixpackage"
            " for help."
        ).format(this_distro))


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
            "Package installation of {0} returned an error code. Try again with: '{1}'"
        ).format(', '.join(generic_package_names), installation_command))


class ConnectionFailure(UnixPackageException):
    pass


class CalledProcessError(UnixPackageException):
    pass