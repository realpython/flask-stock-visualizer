import os
import stat
from urlparse import urlparse
import ConfigParser

# from clint.textui import puts, colored
from werckercli.cli import puts, get_term

import netrc
from werckercli.paths import find_git_root

VALUE_USER_NAME = "user_name"
VALUE_USER_TOKEN = "user_token"
VALUE_USER_NAME = "user_name"
VALUE_PROJECT_ID = "project_id"
VALUE_HEROKU_TOKEN = "heroku_netrc_password"
VALUE_WERCKER_URL = "wercker_url"
VALUE_MIXPANEL_TOKEN = "mixpanel_token"
VALUE_DISPLAY_DEBUG = "display_debug"
# VALUE_DISPLAY_DEBUG = ""

ENV_KEY_WERCKER_URL = "WERCKER_URL"
ENV_KEY_MIXPANEL_TOKEN = "WERCKER_MIXPANEL_TOKEN"
ENV_KEY_DISPLAY_DEBUG = "WERCKER_CLI_DEBUG"

DEFAULT_WERCKER_URL = "https://app.wercker.com"
DEFAULT_DOT_WERCKER_NAME = ".wercker"
DEFAULT_MIXPANEL_TOKEN = "380db8420ac773c58e7c923f5b0dd9b4"
DEFAULT_DISPLAY_DEBUG = False
DEFAULT_WERCKER_YML = "wercker.yml"


def _get_or_create_netrc_location():
    term = get_term()
    try:
        file = os.path.join(os.environ['HOME'], ".netrc")
    except KeyError:
        raise IOError("Could not find .netrc: $HOME is not set")

    if os.path.isfile(file):
        result = os.stat(file)
        mode = oct(stat.S_IMODE(result.st_mode))
        if mode != '0600':
            puts(
                term.yellow('Warning:') +
                'Found permission %s, on %s. It should be 0600' %
                (mode, file)
            )

    else:
        with os.fdopen(os.open(file, os.O_APPEND | os.O_CREAT, 0o600)) as out:
            out.close()

    return file


def get_value(name, default_value=None, path=os.curdir, print_warnings=True):
    value = None
    term = get_term()

    if name == VALUE_WERCKER_URL:
        value = os.getenv("wercker_url", None)
        if value is None:
            value = os.getenv(ENV_KEY_WERCKER_URL, DEFAULT_WERCKER_URL)

        return value

    elif name == VALUE_MIXPANEL_TOKEN:
        value = os.getenv(ENV_KEY_MIXPANEL_TOKEN, DEFAULT_MIXPANEL_TOKEN)

    elif name == VALUE_USER_TOKEN:

        wercker_url = get_value(VALUE_WERCKER_URL)
        url = urlparse(wercker_url)

        file = _get_or_create_netrc_location()
        rc = netrc.netrc(file)

        if url.hostname in rc.hosts:
            value = rc.hosts[url.hostname][2]

    elif name == VALUE_USER_NAME:

        wercker_url = get_value(VALUE_WERCKER_URL)
        url = urlparse(wercker_url)

        file = _get_or_create_netrc_location()
        rc = netrc.netrc(file)

        if url.hostname in rc.hosts:
            value = rc.hosts[url.hostname][0]

    elif name == VALUE_HEROKU_TOKEN:

        file = _get_or_create_netrc_location()
        rc = netrc.netrc(file)

        result = rc.authenticators('api.heroku.com')
        if result and len(result) == 3:
            value = result[2]

    elif name == VALUE_PROJECT_ID:
        # from paths import find_git_root

        path = find_git_root(path)

        if not path:
            if print_warnings:
                puts(
                    term.red("Warning:") +
                    " Could not find a git repository."
                )
            return

        file = os.path.join(
            path,
            DEFAULT_DOT_WERCKER_NAME
        )

        if not os.path.isfile(file):
            if print_warnings:
                puts(
                    term.yellow("Warning:") +
                    " Could not find a %s file in the application root" %
                    DEFAULT_DOT_WERCKER_NAME
                )

            return

        Config = ConfigParser.ConfigParser()

        Config.read(file)

        try:
            value = Config.get('project', 'id')
        except (
            ConfigParser.NoOptionError,
            ConfigParser.NoSectionError
        ):
            value = None

    elif name == VALUE_DISPLAY_DEBUG:
        env_value = os.environ.get(ENV_KEY_DISPLAY_DEBUG)

        if env_value is not None and env_value.lower() == "true":
            value = True
        else:
            value = DEFAULT_DISPLAY_DEBUG

    return value


def set_value(name, value):

    term = get_term()

    if name == VALUE_USER_TOKEN:

        file = _get_or_create_netrc_location()

        rc = netrc.netrc(file=file)

        wercker_url = get_value(VALUE_WERCKER_URL)
        url = urlparse(wercker_url)

        if url.hostname in rc.hosts:
            current_settings = rc.hosts[url.hostname]
        else:
            current_settings = (None, None, None)

        if value is not None:
            rc.hosts[url.hostname] = (
                current_settings[0],
                current_settings[1],
                value
            )
        else:
            rc.hosts.pop(url.hostname)

        with open(file, 'w') as fp:
            fp.write(str(rc))
            fp.close()

    elif name == VALUE_USER_NAME:

        file = _get_or_create_netrc_location()

        rc = netrc.netrc(file=file)

        wercker_url = get_value(VALUE_WERCKER_URL)
        url = urlparse(wercker_url)

        if url.hostname in rc.hosts:
            current_settings = rc.hosts[url.hostname]
        else:
            current_settings = (None, None, None)

        if value is not None:
            rc.hosts[url.hostname] = (
                value,
                current_settings[1],
                current_settings[2])
        else:
            rc.hosts.pop(url.hostname)

        with open(file, 'w') as fp:
            fp.write(str(rc))
            fp.close()

    elif name == VALUE_PROJECT_ID:

        path = find_git_root(os.curdir)

        if not path:
            puts(
                term.red("Error:") +
                " Could not find the root repository."
            )
            return

        file = os.path.join(
            path,
            DEFAULT_DOT_WERCKER_NAME
        )

        Config = ConfigParser.ConfigParser()

        if os.path.isfile(file):

            Config.read(file)

        if not 'project' in Config.sections():
            Config.add_section('project')

        fp = open(file, 'w')
        Config.set('project', 'id', value)

        Config.write(fp)

        fp.close()
