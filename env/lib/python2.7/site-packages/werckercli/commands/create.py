import sys
import textwrap
from werckercli.decorators import login_required

from werckercli.git import (
    get_remote_options,
    convert_to_url,
)

from werckercli import prompt

from werckercli.cli import (
    get_term,
    puts,
    pick_url
)

from werckercli.git import (
    get_preferred_source_type,
    filter_heroku_sources,
    get_source_type,
    get_username,
    get_project,
    SOURCE_BITBUCKET,
    SOURCE_GITHUB,
)

from werckercli.config import (
    set_value,
    get_value,
    VALUE_PROJECT_ID,
    VALUE_WERCKER_URL
)
from werckercli.client import Client
from werckercli.paths import find_git_root

from werckercli.commands.target import add as target_add
from werckercli.commands.project import (
    project_build,
    project_link
)


'''
create an application on wercker
'''


@login_required
def create(path='.', valid_token=None):
    if not valid_token:
        raise ValueError("A valid token is required!")

    term = get_term()

    if get_value(VALUE_PROJECT_ID, print_warnings=False):
        puts("A .wercker file was found.")
        run_create = prompt.yn(
            "Are you sure you want to run `wercker create`?",
            default="n")

        if run_create is False:
            puts("Aborting.")
            return
        else:
            puts("")

    if project_link(
        valid_token=valid_token,
        puts_result=False,
        auto_link=False
    ):
        puts("A matching application was found on wercker.")
        use_link = prompt.yn("Do you want to run 'wercker link' instead of\
 `wercker create`?")

        puts("")

        if use_link is True:
            project_link(valid_token=valid_token)
            return

    path = find_git_root(path)

    if path:
        options = get_remote_options(path)

        heroku_options = filter_heroku_sources(options)
    else:
        options = []
        heroku_options = []

    if not path:
        return False

    puts('''About to create an application on wercker.

This consists of the following steps:
1. Configure application
2. Setup keys
3. Add a deploy target ({heroku_options} heroku targets detected)
4. Trigger initial build'''.format(
        wercker_url=get_value(VALUE_WERCKER_URL),
        heroku_options=len(heroku_options))
    )

    if not path:
        puts(
            term.red("Error:") +
            " Could not find a repository." +
            " wercker create requires a git repository. Create/clone a\
 repository first."
        )
        return

    options = [o for o in options if o not in heroku_options]

    options = [o for o in options if o.priority > 1]

    count = len(options)
    puts('''
Step ''' + term.white('1') + '''. Configure application
-------------
''')
    puts(
        "%s repository location(s) found...\n"
        % term.bold(str(count))
    )

    url = pick_url(options)
    url = convert_to_url(url)

    source = get_preferred_source_type(url)
    puts("\n%s repository detected..." % source)
    puts("Selected repository url is %s\n" % url)

    client = Client()

    code, profile = client.get_profile(valid_token)

    source_type = get_source_type(url)

    if source_type == SOURCE_BITBUCKET:
        if profile.get('hasBitbucketToken', False) is False:
            puts("No Bitbucket account linked with your profile. Wercker uses\
 this connection to linkup some events for your repository on Bitbucket to our\
  service.")
            provider_url = get_value(
                VALUE_WERCKER_URL
            ) + '/provider/add/cli/bitbucket'

            puts("Launching {url} to start linking.".format(
                url=provider_url
            ))
            from time import sleep

            sleep(5)
            import webbrowser

            webbrowser.open(provider_url)

            raw_input("Press enter to continue...")
    elif source_type == SOURCE_GITHUB:
        if profile.get('hasGithubToken', False) is False:
            puts("No GitHub account linked with your profile. Wercker uses\
 this connection to linkup some events for your repository on GitHub to our\
 service.")
            provider_url = get_value(
                VALUE_WERCKER_URL
            ) + '/provider/add/cli/github'

            puts("Launching {url} to start linking.".format(
                url=provider_url
            ))

            from time import sleep

            sleep(5)

            import webbrowser

            webbrowser.open(provider_url)

            raw_input("Press enter to continue...")
    username = get_username(url)
    project = get_project(url)

    puts('''
Step {t.white}2{t.normal}.
-------------
In order to clone the repository on wercker, an ssh key is needed. A new/unique
key can be generated for each repository. There 3 ways of using ssh keys on
wercker:

{t.green}1. Automatically add a deploy key [recommended]{t.normal}
2. Use the checkout key, wercker uses for public projects.
3. Let wercker generate a key, but allow add it manually to github/bitbucket.
(needed when using git submodules)

For more information on this see: http://etc...
'''.format(t=term))
    key_method = None
    while(True):
        result = prompt.get_value_with_default(
            "Options:",
            '1'
        )

        valid_values = [str(i + 1) for i in range(3)]

        if result in valid_values:
            key_method = valid_values.index(result)
            break
        else:
            puts(term.red("warning: ") + " invalid build selected.")

    checkout_key_id = None
    checkout_key_publicKey = None

    if(key_method != 1):
        puts('''Retrieving a new ssh-key.''')
        status, response = client.create_checkout_key()
        puts("done.")

        if status == 200:
            checkout_key_id = response['id']
            checkout_key_publicKey = response['publicKey']

            if key_method == 0:
                puts('Adding deploy key to repository:')
                status, response = client.link_checkout_key(valid_token,
                                                            checkout_key_id,
                                                            username,
                                                            project,
                                                            source_type)
                if status != 200:
                    puts(term.red("Error:") +
                         " uanble to add key to repository.")
                    sys.exit(1)
            elif key_method == 2:
                profile_username = profile.get('username')
                status, response = client.get_profile_detailed(
                    valid_token,
                    profile_username)

                username = response[source_type + 'Username']
                url = None
                if source_type == SOURCE_GITHUB:
                    url = "https://github.com/settings/ssh"
                elif source_type == SOURCE_BITBUCKET:
                    url = "http://bitbucket.org/account/user/{username}/\
ssh-keys/"

                if status == 200:
                    formatted_key = "\n".join(
                        textwrap.wrap(checkout_key_publicKey))

                    puts('''Please add the following public key:
    {publicKey}

    You can add the key here: {url}\n'''.format(publicKey=formatted_key,
                                                url=url.format(
                                                    username=username)))
                    raw_input("Press enter to continue...")
                else:
                    puts(term.red("Error:") +
                         " unable to load wercker profile information.")
                    sys.exit(1)
        else:
            puts(term.red("Error:") + 'unable to retrieve an ssh key.')
            sys.exit(1)

    puts("Creating a new application")
    status, response = client.create_project(
        valid_token,
        username,
        project,
        source,
        checkout_key_id,
    )

    if response['success']:

        puts("done.\n")
        set_value(VALUE_PROJECT_ID, response['data']['id'])

        puts("In the root of this repository a .wercker file has been created\
 which enables the link between the source code and wercker.\n")

        site_url = None

        if source_type == SOURCE_GITHUB:

            site_url = "https://github.com/" + \
                username + \
                "/" + \
                project

        elif source_type == SOURCE_BITBUCKET:

            site_url = "https://bitbucket.org/" + \
                username + \
                "/" + \
                project

        puts('''
Step ''' + term.white('3') + '''.
-------------
''')

        target_options = heroku_options

        nr_targets = len(target_options)
        puts("%s automatic supported target(s) found." % str(nr_targets))

        if nr_targets:
            target_add(valid_token=valid_token)

        puts('''
Step ''' + term.white('4') + '''.
-------------
''')

        project_build(valid_token=valid_token)

        puts('''
Done.
-------------

You are all set up to for using wercker. You can trigger new builds by
committing and pushing your latest changes.

Happy coding!''')
    else:
        puts(
            term.red("Error: ") +
            "Unable to create project. \n\nResponse: %s\n" %
            (response.get('errorMessage'))
        )
        puts('''
Note: only repository where the wercker's user has permissions on can be added.
This is because some event hooks for wercker need to be registered on the
repository. If you want to test a public repository and don't have permissions
 on it: fork it. You can add the forked repository to wercker''')
