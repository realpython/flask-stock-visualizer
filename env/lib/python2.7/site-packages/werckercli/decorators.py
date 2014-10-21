import os

# import enhancedyaml
from yaml import load
from yaml.parser import ParserError

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from werckercli.authentication import get_access_token
from werckercli.cli import puts, get_term
from werckercli.config import DEFAULT_WERCKER_YML
from werckercli.paths import find_git_root


def login_required(f):
    def new_f(*args, **kwargs):
        if not "valid_token" in kwargs:
            token = get_access_token()
            # if token:
            kwargs['valid_token'] = token

        return f(*args, **kwargs)

    new_f.__name__ = f.__name__
    return new_f


def yaml_required(f):
    def new_f(*args, **kwargs):
        if not "path" in kwargs:
            # path = "."
            path = find_git_root(os.curdir)
            kwargs['path'] = path
        if not "str_data" in kwargs:
            yaml = os.path.join(path, DEFAULT_WERCKER_YML)

            if os.path.isfile(yaml):

                fh = open(yaml)
                data = fh.read()
                fh.close()

                kwargs["str_data"] = data
            else:
                term = get_term()
                puts("{t.red}Error:{t.normal} {yaml} not found".format(
                    yaml=DEFAULT_WERCKER_YML,
                    t=term)
                )
        if not "yaml_data" in kwargs and "str_data" in kwargs:

            try:
                yaml_data = load(kwargs["str_data"], Loader=Loader)
            except ParserError:
                yaml_data = None

                term = get_term()
                puts(
                    "{t.red}Error:{t.normal} {yaml} is not formatted propery."
                    .format(
                        t=term,
                        yaml=DEFAULT_WERCKER_YML)
                )

            if type(yaml_data) is dict:
                kwargs["yaml_data"] = yaml_data

        return f(*args, **kwargs)

    new_f.__name__ = f.__name__
    return new_f
