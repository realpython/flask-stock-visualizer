

"""Test for werckercli"""

import sys
import os
import shutil
import tempfile
from werckercli.config import ENV_KEY_WERCKER_URL

from httpretty import HTTPretty

if sys.version_info >= (2, 7):
    # If Python itself provides an exception, use that
    import unittest
    from unittest import TestCase as _TestCase
else:
    import unittest2 as unittest
    from unittest2 import TestCase as _TestCase


from utils import (
    duplicate_repo_folder,
    copy_test_data
)

VALID_TOKEN = '50ffd4a6b4e145006c0000031359019219496'
VALID_GITHUB_SSH_URL = "git@github.com:wercker/wercker-cli.git"
VALID_GITHUB_HTTPS_URL = "https://github.com/wercker/wercker-cli.git"
VALID_BITBUCKET_SSH_URL = "git@bitbucket.org:postmodern/ronin.git"
VALID_BITBUCKET_HTTPS_URL =\
    "https://flenter@bitbucket.org/postmodern/ronin.git"
VALID_HEROKU_SSH_URL = "git@heroku.com:clitest.git"


class TestCase(_TestCase):

    def makeSafeEnv(self):
        """Create environment with homedirectory-related variables stripped.

        Modifies os.environ for the duration of a test case to avoid
        side-effects caused by the user's ~/.gitconfig and other
        files in their home directory.
        """
        old_env = os.environ

        def restore():
            os.environ = old_env

        self.addCleanup(restore)
        new_env = dict(os.environ)

        for e in ['HOME', 'HOMEPATH', 'USERPROFILE']:
            new_env[e] = '/nosuchdir'
        os.environ = new_env

    def setUp(self):
        super(TestCase, self).setUp()
        self.makeSafeEnv()


class TempHomeSettingsCase(TestCase):

    template_name = ""

    def setUp(self):
        super(TempHomeSettingsCase, self).setUp()

        self._initial_folder = os.getcwd()

        self.__home_folder = tempfile.mkdtemp()
        os.environ['HOME'] = self.__home_folder

        if self.template_name:
            copy_test_data(
                self.template_name,
                self.__home_folder
            )

    def tearDown(self):
        os.chdir(self._initial_folder)
        super(TempHomeSettingsCase, self).tearDown()
        shutil.rmtree(self.__home_folder)

    def get_home_folder(self):
        return self.__home_folder


class DataSetTestCase(TempHomeSettingsCase):
    repo_name = 'empty'

    folder = ''

    def setUp(self):
        super(DataSetTestCase, self).setUp()
        self.folder = duplicate_repo_folder(self.repo_name)

    def tearDown(self):
        super(DataSetTestCase, self).tearDown()
        shutil.rmtree(self.folder)

    def get_git_path(self):
        # return self.folder
        return os.path.join(
            self.folder,
            self.repo_name,
            self.get_git_folder()
        )

    def get_git_folder(self, absolute=False):

        folder = self.repo_name
        return folder + ".git"


class BasicClientCase(DataSetTestCase):
    wercker_url = "http://localhost:3000"
    valid_token = VALID_TOKEN

    def setUp(self):
        super(BasicClientCase, self).setUp()

        os.environ[ENV_KEY_WERCKER_URL] = self.wercker_url
        HTTPretty.reset()
        HTTPretty.enable()

    def tearDown(self):
        super(BasicClientCase, self).tearDown()
        HTTPretty.disable()
        HTTPretty.reset()

    def register_api_call(self, path, responses):

        response_objects = []

        for response in responses:
            response_objects.append(
                HTTPretty.Response(**response)
            )

        HTTPretty.register_uri(
            HTTPretty.POST,
            self.wercker_url + '/api/1.0/' + path,
            responses=response_objects
        )


def self_test_suite():
    names = [
        'git',
        'paths',
        'client',
        'authentication',
        'prompt',
        'cli',
        'decorators',
        'heroku',
    ]

    module_names = ['werckercli.tests.test_' + name for name in names]

    loader = unittest.TestLoader()
    return loader.loadTestsFromNames(module_names)


def test_suite():
    result = unittest.TestSuite()
    result.addTests(self_test_suite())

    return result
