import mock
from mock import ANY
import requests
from werckercli.metrics import track_application_startup, default_command_name

from werckercli.tests import TestCase

track_command_usage_path = "werckercli.metrics.track_command_usage"


class MetricsTests(TestCase):

    def test_track_application_startup_fails_silently_on_ConnectionError(self):
        err = requests.ConnectionError()
        the_method = mock.Mock(side_effect=err)

        with mock.patch(track_command_usage_path, the_method) as puts:
            try:
                track_application_startup()
            except requests.ConnectionError:
                self.fail("track_application_startup didn't fail silently")

    def test_track_application_startup_calls_track_command_usage(self):
        the_method = mock.Mock()

        with mock.patch(track_command_usage_path, the_method) as puts:
            the_method.assert_called_once()

    @mock.patch("sys.argv", ['main.py'])
    def test_track_application_startup_uses_default_command_on_empty_arg(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

            the_method.assert_called_with(default_command_name, ANY)

    @mock.patch("sys.argv", ['main.py', 'validate'])
    def test_track_application_startup_passes_command_from_sys_args(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

            the_method.assert_called_with('validate', ANY)

    @mock.patch("sys.argv", [None, 'validate'])
    def test_track_application_startup_handles_missing_script_arg(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

    @mock.patch("sys.argv", [None, 'validate'])
    def test_track_application_startup_handles_missing_script_arg(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

    @mock.patch("sys.argv", [None, 'validate', 'foo', 'bar'])
    def test_track_application_startup_passes_args(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

            expected_args = ['foo', 'bar']
            the_method.assert_called_with(ANY, expected_args)

    @mock.patch("sys.argv", [None, 'validate'])
    def test_track_application_startup_passes_None_for_missing_arguments(self):
        the_method = mock.Mock()
        with mock.patch(track_command_usage_path, the_method) as puts:
            track_application_startup()

            expected_args = None
            the_method.assert_called_with(ANY, expected_args)
