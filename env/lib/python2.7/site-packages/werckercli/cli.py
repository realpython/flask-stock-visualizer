#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import os
import sys

from blessings import Terminal

from werckercli.git import get_priority
from werckercli import prompt

terminal_file_handle = sys.stdout

INFO = "INFO"
DEBUG = "DEBUG"


def get_term():
    return Terminal(stream=terminal_file_handle)


def puts(content, level=INFO):
    if level == INFO:
        terminal_file_handle.write(
            content.encode("utf-8") + '\n'
        )
    elif level == DEBUG:
        from werckercli import config
        if config.get_value(config.VALUE_DISPLAY_DEBUG):
            terminal_file_handle.write(
                "debug:: " + content.encode("utf-8") + '\n'
            )


def get_intro():
    term = get_term()
    intro = 23*u"-"
    intro += u"\n"
    intro += u'welcome to ' + term.green('wercker-cli')
    intro += u"\n"
    intro += 23*u"-"
    intro += u"\n"

    return intro


def handle_commands(args):
    """ Core handler for redirecting to the proper commands."""

    # print args
    from werckercli.commands.create import create\
        as command_create
    from werckercli.commands.project import project_list\
        as command_project_list
    from werckercli.commands.project import project_link\
        as command_project_link
    from werckercli.commands.project import project_build\
        as command_project_build
    from werckercli.commands.build import build_list\
        as command_builds_list
    from werckercli.commands.build import build_deploy\
        as command_builds_deploy
    from werckercli.commands.target import add\
        as command_add
    from werckercli.commands.target import list_by_project\
        as command_list_by_project
    from werckercli.commands.target import link_to_deploy_target\
        as command_target_details
    from werckercli.commands.clearsettings import clear_settings\
        as command_clear_settings
    from werckercli.commands.login import login\
        as command_login
    from werckercli.commands.project import project_list_queue\
        as command_list_jobs
    from werckercli.commands.project import project_open\
        as command_project_open
    from werckercli.commands.services import search_services\
        as command_search_services
    from werckercli.commands.services import info_service\
        as command_info_service
    from werckercli.commands.services import list_services\
        as command_list_services
    from werckercli.commands.update import update\
        as command_update
    from werckercli.commands.validate import validate\
        as command_validate
    from werckercli.commands.services import add_service\
        as command_add_service
    from werckercli.commands.services import remove_service\
        as command_remove_service

    try:
        if args.get('apps') and args.get('create'):
            command_create()
        elif args.get('create'):
            command_create()
        elif args.get('status'):
            command_builds_list(limit=1)
        elif args.get('deploy'):
            command_builds_deploy()
        elif args.get('apps'):
            # if args['list']:
            if args.get('build'):
                command_project_build()
            else:
                command_project_list()
        elif args.get('link'):
            command_project_link()
            # elif args.get("build"):
            #     command_project_build()
        elif args.get("builds"):
            # if args['list']:
            command_builds_list()
            # if args['deploy']:
                # command_builds_deploy()
        elif args.get('targets'):
            if args.get('add'):
                command_add()
            elif args.get('list'):
                command_list_by_project()
            elif args.get('details') or args.get('open'):
                command_target_details()
        elif args.get('open'):
            command_project_open()
        elif args.get('validate'):
            command_validate()
        elif args.get('login'):
            command_login()
        elif args.get('logout'):
            command_clear_settings()
        elif args.get('services'):
            if args.get('search'):
                command_search_services(args.get('<name>'))
            elif args.get('info'):
                version = args.get('<version>')

                if version is None:
                    version = 0

                command_info_service(
                    args.get('<name>'),
                    version=version
                )
            elif args.get('add'):
                version = args.get('<version>')
                if version is None:
                    version = 0

                command_add_service(
                    args.get('<name>'),
                    version=version
                )
            elif args.get('remove'):
                command_remove_service(
                    args.get('<name>'),
                )
            else:
                command_list_services()

        elif args.get('queue'):
            command_list_jobs()
        elif args.get('update'):
            command_update()
    except KeyboardInterrupt:
        puts("\nAborted...")


def enter_url(loop=True):
    """Get an url and validate it, asks confirmation for unsupported urls"""

    term = get_term()

    while True:

        url = raw_input("Enter a repository url:")

        if url != "":
            if get_priority(url, "custom") == 0:
                puts(
                    term.yellow("Warning:") +
                    " This is not a valid ssh url for github/bitbucket."
                )

                sure = prompt.yn(
                    "Are you sure you want to use this url?",
                    default="n"
                )
                if not sure:
                    url = ""
                else:
                    return url
            else:
                return url

        if not loop:
            return


def pick_url(options, allow_custom_input=False):
    """Allows the user to pick one of the options or enter a new locaiton"""

    term = get_term()

    puts(
        "Please choose one of the following options: ")

    index = 1
    enter_custom_choice = 1
    default_choice = 1

    for option in options:
        if(option.priority < 1):
            puts(' (%d) %s ' % (index, term.red(option.url)))
            if(default_choice == index):
                default_choice += 1
        else:
            to_print = ' (%d) %s ' % (index, option.url)

            if(index == default_choice):
                to_print = term.green(to_print)
            puts(to_print)
        index += 1

    enter_custom_choice = len(options) + 1

    if allow_custom_input:
        puts(' (%d) enter a new location' % index)

    def option_to_str(i):
        if not i == default_choice:
            return str(i)
        else:
            return str(i) + "=default"

    if allow_custom_input:
        choices = map(
            option_to_str,
            range(1, index + 1)
        )
    else:
        choices = map(
            option_to_str,
            range(1, index)
        )

    while True:

        url = None

        choice = raw_input(
            "Make your choice (%s): " % (
                ",".join(choices),
            )
        )

        selected = None

        if choice == "":
            selected = default_choice
        elif choice in choices:
            selected = choice

            try:
                selected = int(choice)
            except ValueError:
                selected = None

        elif choice == str(default_choice):
            selected = default_choice

        if selected:
            if allow_custom_input and selected == enter_custom_choice:
                url = enter_url()
            else:
                url = options[selected-1].url

            if url:
                return url


def pick_project_name(url):

    project = os.path.basename(url).split(".")[0]

    puts("Detecting project name...")

    return prompt.get_value_with_default("Enter project name: ", project)
