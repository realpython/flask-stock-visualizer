import os

WERCKER_FOLDER_NAME = '.wercker'
WERCKER_CREDENTIALS_FILE = 'credentials'


def get_global_wercker_path():
    return os.path.join(os.environ['HOME'], WERCKER_FOLDER_NAME)


def get_global_wercker_filename():
    return os.path.join(get_global_wercker_path(), WERCKER_CREDENTIALS_FILE)


def check_or_create_path(path):
    if not os.path.isdir(path):
        os.makedirs(path)

    return True


def find_folder_containing_folder_name(path, folder_name):
    """Find the nearest parent with a <folder_name> folder"""

    if path == os.path.curdir:
        path = os.path.realpath(path)

    if os.path.isdir(path):
        if os.path.isdir(os.path.join(path, folder_name)):
            return path
        else:
            parent = os.path.realpath(os.path.join(path, os.path.pardir))
            if parent == path:
                return None
            return find_folder_containing_folder_name(parent, folder_name)


def find_git_root(path, folder_name=".git"):
    """
        Find the nearest parent with <folder_name> folder, handy for
        locating the ".git" root folder
    """
    return find_folder_containing_folder_name(path, folder_name)
