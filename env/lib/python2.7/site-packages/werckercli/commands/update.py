try:
    from cStringIO import StringIO
    import xmlrpclib
except ImportError:
    from io import StringIO
    import xmlrpc.client as xmlrpclib

import werckercli
from werckercli.cli import puts, get_term

import semantic_version as semver


def find_current_version(package, cur_version, index_urls=None):

    if index_urls is None:
        index_urls = ['http://pypi.python.org/pypi']

    for index_url in index_urls:
        pypi = xmlrpclib.ServerProxy(index_url, xmlrpclib.Transport())
        pypi_hits = pypi.package_releases(package)
        if len(pypi_hits) > 0:
            if semver.Version(pypi_hits[0]) > cur_version:
                return semver.Version(pypi_hits[0])

    return False


def update(current_version=None):

    term = get_term()

    if current_version is None:
        current_version = werckercli.__version__

    current_version = semver.Version(current_version)

    newer_version = find_current_version(
        "wercker",
        current_version
    )

    if newer_version:
        puts("""A newer version of the wercker-cli was found ({newer_version}).
Please upgrade:
""".format(newer_version=newer_version) +
            term.bold_white('pip install wercker --upgrade')
        )
        return True

    else:
        puts("Current version is up-to-date ({version})".format(
            version=current_version))

        return False
