import os
import unittest

from mock import patch, MagicMock

from actions_cli.cli import (
    _check_call,
    ErrorExit
)


class CheckCallTests(unittest.TestCase):
    @patch('actions_cli.cli.subprocess')
    def test_check_call(self, ms):
        log = MagicMock()
        _check_call(['juju', 'version'], log)
        ms.check_output.called_with(
            ['juju', 'version'],
            cwd=os.path.abspath('.'),
            stderr=None,
            env=os.environ
        )

    @patch('actions_cli.cli.subprocess')
    def test_check_call_opts(self, ms):
        log = MagicMock()
        _check_call(['juju', 'version'], log, cwd='/tmp', stderr=False)
        ms.check_output.called_with(
            ['juju', 'version'],
            cwd='/tmp',
            stderr=False,
            env=os.environ
        )

    @patch('actions_cli.cli.subprocess')
    def test_check_call_failure(self, ms):
        log = MagicMock()
        ms.CalledProcessError = Exception
        ms.check_output.side_effect = ms.CalledProcessError()
        self.assertRaises(ErrorExit, _check_call, ['juju', 'version'], log)
        self.assertEqual(1, len(ms.check_output.mock_calls))

    @patch('actions_cli.cli.subprocess')
    @patch('actions_cli.cli.time')
    def test_check_call_failure_opts(self, msl, ms):
        log = MagicMock()
        log2 = MagicMock()
        ms.CalledProcessError = Exception
        ms.check_output.side_effect = [ms.CalledProcessError()]
        self.assertRaises(ErrorExit, _check_call, ['juju', 'version'], log,
                          max_retry=3)
        self.assertEqual(4, len(ms.check_output.mock_calls))
        self.assertEqual(None, _check_call(['juju', 'version'], log2,
                                           ignoreerr=True))
        log2.error.assert_not_called()


class BaseEnvironmentTests(unittest.TestCase):
    pass
