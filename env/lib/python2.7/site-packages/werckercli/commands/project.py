import os

from werckercli.decorators import login_required
from werckercli.git import (
    get_remote_options,
    convert_to_url,
)

from werckercli import prompt
from werckercli.cli import get_term, puts
from werckercli.client import Client
from werckercli.paths import find_git_root
from werckercli.printer import (
    print_hr,
    print_line,
    store_highest_length,
    format_date
)
from werckercli.config import (
    get_value,
    set_value,
    VALUE_PROJECT_ID,
    VALUE_WERCKER_URL
)

from werckercli.commands.build import get_builds, print_builds
from werckercli.commands.target import get_targets


def project_open():
    project_id = get_value(VALUE_PROJECT_ID, print_warnings=False)

    term = get_term()

    if not project_id:
        puts(
            term.red("Error: ") +
            "No application found. Please create or link an application first"
        )
        return

    wercker_url = get_value(VALUE_WERCKER_URL)

    link = "{wercker_url}/#project/{project_id}".format(
        wercker_url=wercker_url,
        project_id=project_id
    )
    puts("Opening link: {link}".format(link=link))
    import webbrowser

    webbrowser.open(link)


@login_required
def project_list(valid_token=None):

    if not valid_token:
        raise ValueError("A valid token is required!")

    c = Client()

    response, result = c.get_applications(valid_token)

    header = ['name', 'author', 'status', 'followers', 'url']
    props = [
        'name',
        'author',
        'status',
        'totalFollowers',
        'url'
    ]

    max_lengths = []

    for i in range(len(header)):
        max_lengths.append(0)

    store_highest_length(max_lengths, header)

    puts("Found %d result(s)...\n" % len(result))
    for row in result:
        store_highest_length(max_lengths, row, props)

    result = sorted(result, key=lambda k: k['name'])
    print_hr(max_lengths, first=True)
    print_line(max_lengths, header)
    print_hr(max_lengths)

    for row in result:
        print_line(max_lengths, row, props)
    print_hr(max_lengths)


@login_required
def project_link(valid_token=None, puts_result=True, auto_link=True):

    if not valid_token:
        raise ValueError("A valid token is required!")

    term = get_term()

    if puts_result:
        puts("Searching for git remote information... ")

    path = find_git_root(os.curdir)

    if not path:
        if puts_result:
            puts(term.red("error:") + " No git repository found")
        return False

    options = get_remote_options(path)

    if options is None:
        if puts_result:
            puts(term.red("error:") + " No git repository found")
        return False

    if puts_result:
        puts("Retrieving list of applications...")

    c = Client()

    response, result = c.get_applications(valid_token)

    for option in options:
        for app in result:

            if convert_to_url(app['url']) == convert_to_url(option.url):

                if auto_link:
                    set_value(VALUE_PROJECT_ID, app['id'])

                if puts_result:
                    puts(
                        term.green("success:") +
                        " application is now linked to this repository"
                    )
                return True

    if puts_result:
        puts(
            "An application could " + term.white("not") +
            " be linked to this repository")
    return False


@login_required
def project_build(valid_token=None):
    if not valid_token:
        raise ValueError("A valid token is required!")

    term = get_term()

    puts("Triggering a new build.")

    c = Client()
    code, response = c.trigger_build(valid_token, get_value(VALUE_PROJECT_ID))

    if response['success'] is False:
        if "errorMessage" in response:
            puts(term.red("Error: ") + response['errorMessage'])
        else:
            puts("Unable to trigger a build on the default/master branch")

        return False
    else:
        puts("done.")
        return True
    # print code, response


@login_required
def project_list_queue(valid_token=None):

    term = get_term()

    if not valid_token:
        raise ValueError("A valid token is required!")

    project_id = get_value(VALUE_PROJECT_ID, print_warnings=False)

    if not project_id:
        puts(
            term.red("Error: ") +
            "No application found. Please create or link an application first"
        )
        return

    term = get_term()

    puts("Retrieving list of unfinished builds.")

    result = get_builds(valid_token, project_id)

    unknowns = filter(lambda r: r['result'] == "unknown", result)

    print_builds(unknowns)
    # print unknowns

    result = get_targets(valid_token, project_id)

    for target in result['data']:
        # print target['id']
        c = Client()
        code, deploys = c.get_deploys(valid_token, target['id'])

        # print result
        # puts("Target: " + term.yellow(target['name']))

        if 'data' in deploys:

            unknowns = filter(
                lambda d: d['result'] == 'unknown',
                deploys['data']
            )

            puts(("\nFound {amount} scheduled deploys for {target}").format(
                amount=len(unknowns),
                target=term.white(target['name'])
            ))

            print_deploys(unknowns)

    else:
        puts("\nNo scheduled deploys found.")
    # print "List of scheduled deploys:"


def print_deploys(deploys, print_index=False):

    for data in deploys:
        if 'creationDate' in data:
            data['creationDate'] = \
                format_date(data['creationDate'])

        if "progress" in data:
            data['progress'] = "{progress:.1f}%".format(
                progress=data['progress'])

        if "user" in data:
            data["user_name"] = data["user"]["name"]
            data["user_type"] = data["user"]["type"]

    header = [
        'result',
        'progress',
        'deploy by',
        'created',
    ]

    props = [
        'result',
        'progress',
        'user_name',
        'creationDate',
    ]

    if print_index:
        header = [''] + header
        props = ['index'] + props

    max_lengths = []

    for i in range(len(header)):
        max_lengths.append(0)

    store_highest_length(max_lengths, header)

    index = 0

    for row in deploys:
        if print_index:
            row['index'] = index + 1
        index += 1
        store_highest_length(max_lengths, row, props)

    print_hr(max_lengths, first=True)
    print_line(max_lengths, header)
    print_hr(max_lengths)

    for row in deploys:
        print_line(max_lengths, row, props)
    print_hr(max_lengths)
