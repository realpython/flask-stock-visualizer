import mock

from werckercli import prompt
from werckercli.tests import (
    BasicClientCase,
)


class YNTests(BasicClientCase):

    @mock.patch('__builtin__.raw_input', mock.Mock(return_value='y'))
    def test_input_is_y(self):

        result = prompt.yn("are you sure?", default='y')
        self.assertTrue(result)

        result = prompt.yn("are you sure?", default='n')
        self.assertTrue(result)

        result = prompt.yn("are you sure?", default='faulty')
        self.assertTrue(result)

    @mock.patch('__builtin__.raw_input', mock.Mock(return_value=''))
    def test_input_is_nothing(self):

        result = prompt.yn("are you sure?", default='y')
        self.assertTrue(result)

        result = prompt.yn("are you sure?")
        self.assertTrue(result)

        result = prompt.yn("are you sure?", default='n')
        self.assertFalse(result)

        result = prompt.yn("are you sure?", default='faulty')
        self.assertTrue(result)

    @mock.patch('__builtin__.raw_input', mock.Mock(return_value='n'))
    def test_input_is_n(self):

        result = prompt.yn("are you sure?", default='y')
        self.assertFalse(result)

        result = prompt.yn("are you sure?", default='n')
        self.assertFalse(result)
