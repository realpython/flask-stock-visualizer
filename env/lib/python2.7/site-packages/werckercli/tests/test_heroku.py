import mock
from werckercli.tests import (
    TestCase,
    TempHomeSettingsCase,
    # VALID_TOKEN
)

from werckercli import heroku

HEROKU_VERSION_STRING = "HEROKU_TEST_VERSION_STRING"


class StdOutMock:

    def readLines(self):
        return HEROKU_VERSION_STRING


class PopenMock:
    def __init__(self, *args, **kwargs):
        # super(PopenMock, self).__init__(*args, **kwargs)

        self.stdout = StdOutMock()


class IsToolbeltInstalledTests(TestCase):

    def test_is_command_available(self):
        result = heroku.is_toolbelt_installed(
            default_command=['ls', '-la'],
            default_test_string='total '
        )

        self.assertTrue(result)

    def test_is_not_right_command(self):
        result = heroku.is_toolbelt_installed(
            default_command=['cat', '/dev/null'],
            default_test_string='fail'
        )
        self.assertFalse(result)

    def test_command_not_found(self):
        result = heroku.is_toolbelt_installed(
            default_command=['commandDOESNOTexist_doesIt', '-la'],
            default_test_string='fail'
        )
        self.assertFalse(result)


class GetTokenNoTests(TempHomeSettingsCase):

    def test_no_token(self):
        result = heroku.get_token()

        self.assertEqual(result, None)


class GetTokenYesTests(TempHomeSettingsCase):
    template_name = "home-with-netrc"

    @mock.patch(
        'werckercli.heroku.get_value',
        mock.Mock(return_value="1234567890123456789912345678901234567890")
    )
    def test_token_available(self):
        result = heroku.get_token()

        self.assertEqual(result, "1234567890123456789912345678901234567890")
