from fabric.api import local, settings, abort
from fabric.contrib.console import confirm


def test():
    with settings(warn_only=True):
        result = local("heroku run python tests", capture=True)
    if result.failed and not confirm("Tests failed. Continue?"):
        abort("Aborted at user request.")


def deploy():
    test()
    local("git push dokku master")


def commit():
    commit_message = raw_input("Enter a git commit message: ")
    local("git add -A && git commit -am '{}'".format(commit_message))


def push():
    local("git branch")
    branch = raw_input("Which branch do you want to push to? ")
    local("git push origin {}".format(branch))
