import os

from werckercli import git
from werckercli import heroku
from werckercli.printer import (
    store_highest_length,
    print_line, print_hr,
    format_date
)

from werckercli.config import get_value, VALUE_PROJECT_ID, VALUE_WERCKER_URL
from werckercli.decorators import login_required
from werckercli.client import Client
from werckercli.prompt import get_value_with_default
from werckercli.cli import get_term, puts, DEBUG


@login_required
def add(valid_token=None):
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

    options = git.find_heroku_sources(os.curdir)

    if len(options) == 0:
        puts(term.red("Error: ") + "No heroku remotes found")
    elif len(options) == 1:
        _add_heroku_by_git(valid_token, project_id, options[0].url)


def _add_heroku_by_git(token, project_id, git_url):
    term = get_term()
    puts("Heroku remote %s selected." % git_url)

    puts("Looking for Heroku API key...", level=DEBUG)
    heroku_token = heroku.get_token()

    if not heroku_token:
        puts(term.red("Error: "))
        # with indent(2):
        puts("  Please make sure the heroku-toolbelt is installed")
        puts("  and you are loged in.")
        return

    puts("API key found...", level=DEBUG)
    puts("Retrieving applications from Heroku...", level=DEBUG)

    # fp = open("werckercli/tests/data/apps.response.json")
    # import json
    # apps = json.load(fp)
    # fp.close()
    apps = heroku.get_apps()

    preferred_app = None
    for app in apps:
        # print app
        if app['git_url'] == git_url:
            # print app['name']
            # print app
            preferred_app = app

    if not preferred_app:
        raise ValueError(
            "No matching heroku remote repository found in the \
apps for current heroku user"
        )

    c = Client()

    code, result = c.create_deploy_target(
        token,
        project_id,
        preferred_app['name'],
        heroku_token
    )

    if 'success' in result and result['success'] is True:
        puts("Heroku deploy target %s \
successfully added to the wercker application\n" % preferred_app['name'])

    elif result['errorMessage']:
        puts(term.red("Error: ") + result['errorMessage'])
        puts("Please check if the wercker addon was added to the heroku\
application or run heroku addons:add wercker")


def get_targets(valid_token, project_id):
    c = Client()

    puts("\nRetrieving list of deploy targets...")
    code, result = c.get_deploy_targets_by_project(
        valid_token,
        project_id
    )

    return result


def print_targets(targets, print_index=False):

    result = targets

    if 'data' in result:
        for data in result['data']:
            if 'deployFinishedOn' in data:
                data['deployFinishedOn'] = \
                    format_date(data['deployFinishedOn'])

            if 'commitHash' in data:
                data['commitHash'] = data['commitHash'][:8]

    header = [
        'target',
        'result',
        'deploy by',
        'deployed on',
        'branch',
        'commit',
        # 'status',
        'message'
    ]

    props = [
        'name',
        'deployResult',
        'deployBy',
        'deployFinishedOn',
        'branch',
        'commitHash',
        # 'deployStatus',
        'commitMessage',
    ]

    if print_index:
        header = [''] + header
        props = ['index'] + props

    max_lengths = []

    for i in range(len(header)):
        max_lengths.append(0)

    store_highest_length(max_lengths, header)

    if 'data' in result:
        puts("Found %d result(s)...\n" % len(result['data']))
        index = 0
        for row in result['data']:
            if print_index:
                row['index'] = index + 1
            index += 1
            store_highest_length(max_lengths, row, props)

        print_hr(max_lengths, first=True)
        print_line(max_lengths, header)
        print_hr(max_lengths)

        for row in result['data']:
            print_line(max_lengths, row, props)
        print_hr(max_lengths)


def pick_target(valid_token, projectId):
    term = get_term()
    targets = get_targets(valid_token, projectId)

    if not "data" in targets or len(targets['data']) == 0:
        # print targets['data']
        puts(term.red("No targets to deploy to were found"))
        return

    print_targets(targets, print_index=True)

    while(True):
        result = get_value_with_default("Select a target to deploy to", '1')

        valid_values = [str(i + 1) for i in range(len(targets['data']))]

        if result in valid_values:
            target_index = valid_values.index(result)
            break
        else:
            puts(term.yellow("Warning: ") + " invalid target selected.")

    return targets['data'][target_index]['id']


@login_required
def list_by_project(valid_token=None):
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
    targets = get_targets(valid_token, project_id)

    print_targets(targets)


@login_required
def link_to_deploy_target(valid_token=None):
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

    target = pick_target(valid_token, project_id)

    if not target:
        return

    wercker_url = get_value(VALUE_WERCKER_URL)

    link = "{wercker_url}/deploytarget/{target}".format(
        wercker_url=wercker_url,
        target=target
    )
    puts("Opening link: {link}".format(link=link))
    import webbrowser

    webbrowser.open(link)
