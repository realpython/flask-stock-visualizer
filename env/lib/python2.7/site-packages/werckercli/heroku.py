import subprocess
import json

import requests

from config import get_value, VALUE_HEROKU_TOKEN


def is_toolbelt_installed(
    default_command=["heroku", "--version"],
    default_test_string="heroku-toolbelt"
):

    try:
        p = subprocess.Popen(
            default_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except OSError:
        return False

    version_info = p.stdout.readlines()
    p.kill()

    if len(version_info):
        return version_info[0].startswith(default_test_string)

    return False


def get_token():
    return get_value(VALUE_HEROKU_TOKEN)


def get_apps():

    result = requests.get(
        'https://api.heroku.com/apps',
        headers={'Accept': 'application/json'}
    )

    if result.status_code != 200:
        raise IOError(
            "No Status OK returned by heroku (got status=%d) " %
            result.status_code
        )

    return json.loads(result.text)
