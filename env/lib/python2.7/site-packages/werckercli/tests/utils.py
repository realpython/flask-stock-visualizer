import os
import shutil
import tempfile

# from dulwich.repo import Repo

# def open_repo(name):
#     """Open a copy of a repo in a temporary directory."""

#     temp_repo_dir = duplicate_repo_folder(name)
#     return Repo(temp_repo_dir)

# def tear_down_repo(repo):
#     """Tear down a test repository."""

#     temp_dir = os.path.dirname(repo.path.rstrip(os.sep))
#     remove_repo_folder(temp_dir)


def duplicate_repo_folder(name):
    """Duplicate a repo folder"""

    temp_dir = tempfile.mkdtemp()
    repo_dir = os.path.join(
        'repos',
        name
    )
    temp_repo_dir = os.path.join(temp_dir, name)

    copy_test_data(repo_dir, temp_repo_dir)

    return temp_dir


def copy_test_data(subfolder, destination):
    source_dir = os.path.join(
        os.path.dirname(__file__),
        'data',
        subfolder
    )

    # temp_repo_dir = os.path.join(temp_dir, name)
    copytree(source_dir, destination, symlinks=True)


def remove_repo_folder(temp_dir):
    """Remove a duplicated
    folder"""
    shutil.rmtree(temp_dir)


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or \
                os.stat(src).st_mtime - \
                    os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)
