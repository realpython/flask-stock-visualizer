# import os
from httpretty import HTTPretty
# from mock import MagicMock, patch, Mock, create_autospec
import json
import mock

from werckercli.tests import (
    BasicClientCase,
    VALID_TOKEN,
)

from werckercli.client import (
    PATH_BASIC_ACCESS_TOKEN
)

from werckercli import authentication


class DoLoginTests(BasicClientCase):

    @mock.patch(
        'werckercli.authentication.getpass',
        mock.Mock(return_value='test')
    )
    @mock.patch('__builtin__.raw_input', mock.Mock(return_value='test'))
    @mock.patch('werckercli.authentication.puts', mock.Mock())
    @mock.patch('werckercli.authentication.client.puts', mock.Mock())
    def test_do_Login(self):

        self.register_api_call(
            PATH_BASIC_ACCESS_TOKEN,
            [
                {
                    'body':
                    json.dumps(
                        {
                            "success": True,
                            "result":
                            {
                                "token": self.valid_token
                            }
                        }
                    ),
                    'status': 200
                },
                {
                    'body':
                    json.dumps(
                        {
                            "success": True,
                            "result":
                            {
                                "token": self.valid_token + "1"
                            }
                        }
                    ),
                    'status': 200
                },
            ]
        )

        my_authentication = authentication

        with mock.patch('werckercli.cli.puts', mock.Mock):
            # my_authentication = reload(authentication)
            # from werckercli.cli import puts

            # print fake_puts, puts
            result = my_authentication.do_login()

        self.assertEqual(result, self.valid_token)

        result = my_authentication.do_login()

        self.assertEqual(result, self.valid_token + "1")

    @mock.patch(
        'werckercli.authentication.getpass',
        mock.Mock(return_value='test')
    )
    @mock.patch('__builtin__.raw_input', mock.Mock(return_value='test'))
    @mock.patch('werckercli.authentication.puts', mock.Mock())
    @mock.patch('werckercli.authentication.client.puts', mock.Mock())
    def test_do_login_retry_test(self):
        self.register_api_call(
            PATH_BASIC_ACCESS_TOKEN,
            [
                {
                    'body':
                    json.dumps(
                        {
                            "success": False,
                            "result":
                            {
                                "token": self.valid_token
                            }
                        }
                    ),
                    'status': 404
                },
                {
                    'body':
                    json.dumps(
                        {
                            "success": False,
                            "result":
                            {
                                "token": self.valid_token + "1"
                            }
                        }
                    ),
                    'status': 404
                },
                {
                    'body':
                    json.dumps(
                        {
                            "success": True,
                            "result":
                            {
                                "token": self.valid_token
                            }
                        }
                    ),
                    'status': 200
                },
            ]
        )
        # my_authentication = reload(authentication)
        my_authentication = authentication
        result = my_authentication.do_login()
        self.assertEqual(result, self.valid_token)
        self.assertEqual(len(HTTPretty.latest_requests), 3)


class GetAccessTokenTests(BasicClientCase):
    """docstring for GetAccessTokenTests"""

    def setUp(self):
        super(GetAccessTokenTests, self).setUp()
        self.register_api_call(
            PATH_BASIC_ACCESS_TOKEN,
            [
                {
                    'body':
                    json.dumps(
                        {
                            "success": True,
                            "result":
                            {
                                "token": self.valid_token
                            }
                        }
                    ),
                    'status': 200
                },
                {
                    'body':
                    json.dumps(
                        {
                            "success": True,
                            "result":
                            {
                                "token": "invalid"
                            }
                        }
                    ),
                    'status': 200
                },
            ]
        )

    @mock.patch(
        'werckercli.authentication.puts',
        mock.Mock()
    )
    @mock.patch('werckercli.authentication.do_login',
                mock.Mock(return_value=VALID_TOKEN))
    def test_new_login(self):

        my_authentication = authentication
        result = my_authentication.get_access_token()
        self.assertEqual(result, self.valid_token)

    @mock.patch(
        'werckercli.authentication.getpass',
        mock.Mock(return_value='test')
    )
    @mock.patch(
        '__builtin__.raw_input',
        mock.Mock(return_value='test')
    )
    @mock.patch(
        'werckercli.authentication.client.puts',
        mock.Mock()
    )
    @mock.patch(
        'werckercli.authentication.puts',
        mock.Mock()
    )
    def test_login_again(self):
        self.test_new_login()

        # login again
        self.test_new_login()

    @mock.patch('werckercli.authentication.puts', mock.Mock(return_value=None))
    @mock.patch(
        'werckercli.authentication.get_value',
        mock.Mock(return_value=None)
    )
    @mock.patch(
        'werckercli.authentication.do_login',
        mock.Mock(return_value=None)
    )
    def test_login_failed(self):

        # my_authentication = reload(authentication)
        my_authentication = authentication

        with mock.patch(
            "werckercli.authentication.do_login",
            mock.Mock(return_value=None)
        ):
            result = my_authentication.get_access_token()
            self.assertEqual(result, None)
