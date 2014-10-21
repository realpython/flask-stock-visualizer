import os
import random
import mock

from werckercli import config
from werckercli.config import ENV_KEY_WERCKER_URL

from werckercli.tests import BasicClientCase


class GetValueTests(BasicClientCase):
    template_name = "home-with-netrc"
    repo_name = "multiple-remotes"

    def setUp(self, *args, **kwargs):
        self.wercker_url = "http://localhost:" + str(random.randint(1, 65536))
        super(GetValueTests, self).setUp(*args, **kwargs)


class GetValueUrlTests(GetValueTests):
    def test_get_value_wercker_url(self):
        os.environ[ENV_KEY_WERCKER_URL] = self.wercker_url

        result = config.get_value(config.VALUE_WERCKER_URL)
        self.assertEqual(result, self.wercker_url)

        del os.environ[ENV_KEY_WERCKER_URL]

        result = config.get_value(config.VALUE_WERCKER_URL)
        self.assertEqual(result, config.DEFAULT_WERCKER_URL)

    def test_get_value_heroku_token(self):

        with mock.patch("werckercli.config.puts", mock.Mock()) as puts:
            # reload(config)
            result = config.get_value(config.VALUE_HEROKU_TOKEN)

            self.assertEqual(puts.call_count, 1)
            calls = puts.call_args_list
            self.assertTrue('0600' in calls[0][0][0])
        self.assertEqual(result, '1234567890123456789912345678901234567890')

        os.environ.pop('HOME')

        self.assertRaises(IOError, config.get_value, config.VALUE_HEROKU_TOKEN)

    @mock.patch("werckercli.config.puts", mock.Mock())
    def test_get_value_project_id(self):

        os.chdir(self.get_git_path())
        result = config.get_value(config.VALUE_PROJECT_ID)
        self.assertEqual(result, None)
        # self.assertRaises(
        #     NotImplementedError,
        #     config.get_value,
        #     config.VALUE_PROJECT_ID
        # )


class GetValueTokenTests(GetValueTests):
    wercker_url = config.DEFAULT_WERCKER_URL

    def test_get_value_user_token(self):
        with mock.patch("werckercli.config.puts", mock.Mock()):
            # reload(config)

            result = config.get_value(config.VALUE_USER_TOKEN)

        self.assertEqual(result, "'1234567890123456789912345678901234567890'")


class SetValueTests(BasicClientCase):
    template_name = 'home-with-netrc'
    repo_name = "multiple-remotes"

    def test_set_value_user_token(self):
        with mock.patch("werckercli.config.puts", mock.Mock()):
            # reload(config)

            config.set_value(config.VALUE_USER_TOKEN, "test@password")
            self.assertEqual(
                config.get_value(config.VALUE_USER_TOKEN),
                'test@password'
            )

    def _test_set_value_project_id(self):
        self.assertRaises(
            NotImplementedError,
            config.set_value,
            config.VALUE_PROJECT_ID,
            "project_id"
        )
