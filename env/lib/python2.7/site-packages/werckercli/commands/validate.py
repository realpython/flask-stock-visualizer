import os
import shutil

from werckercli.cli import get_term, puts

from werckercli import prompt
from werckercli.paths import find_git_root

import json


def validate():
    """
    Validates the wercker.json file by doing the following:
    * Check whether there is a git repository in the current directory or up.
    * Check whether there is a wercker.json file in that root.
    * Check whether the size of that file is greater that zero.
    * Check whether the wercker.json file contains valid json.

    Currently this command doesn't validate the wercker.json file against
    a schema. But you can expect this in the future.
    """
    term = get_term()
    git_root_path = find_git_root(os.curdir)

    if not git_root_path:
        puts(term.red("Error: ") + "Could not find a git repository")
        return

    wercker_json_path = os.path.join(git_root_path, "wercker.json")
    if os.path.exists(wercker_json_path) is False:
        puts(term.yellow("Warning: ") + " Could not find a wercker.json file")
        return

    if os.path.getsize(wercker_json_path) == 0:
        puts(term.red("Error: ") + "wercker.json is found, but empty")
        return

    try:
        with open(wercker_json_path) as f:
            try:
                json.load(f)

                puts(term.green("wercker.json is found and valid!"))
            except ValueError as e:
                puts(term.red("Error: ") + "wercker.json is not valid json: " +
                     e.message)
    except IOError as e:
        puts(term.red("Error: ") + "Error while reading wercker.json file: " +
             e.message)
