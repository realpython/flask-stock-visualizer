from getpass import getpass

from werckercli.cli import get_term, puts

from werckercli import client
from werckercli.config import (
    get_value,
    set_value,
    VALUE_USER_TOKEN,
    VALUE_USER_NAME
)


def do_login(retry_count=2):
    term = get_term()

    username = raw_input("username: ")
    password = getpass("password: ")

    cl = client.Client()
    status, content = cl.request_oauth_token(username, password)

    if status == 200 and content.get('success', False):
        puts(term.green("Login successful.") + " Welcome %s!" % username)
        set_value(VALUE_USER_NAME, username)

        return content['result']['token']

    elif retry_count > 0:

        puts(
            term.yellow("Warning: ") +
            "Login/password incorrect, please try again.\n")
        return do_login(retry_count - 1)


def get_access_token():

    token = get_value(VALUE_USER_TOKEN)

    if not token:
        token = do_login()

        if not token:
            return

        set_value(VALUE_USER_TOKEN, token)
    return token
