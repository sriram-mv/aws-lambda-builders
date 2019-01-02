from unittest import TestCase

import mock
from parameterized import parameterized

from aws_lambda_builders.exceptions import MisMatchRuntimeError
from aws_lambda_builders.workflows.ruby_bundler.validator import RubyRuntimeValidator


class MockSubProcess(object):

    def __init__(self, returncode):
        self.returncode = returncode

    def communicate(self):
        pass


class TestRubyRuntimeValidator(TestCase):

    def setUp(self):
        self.validator = RubyRuntimeValidator(runtime='ruby2.5', runtime_path='/usr/bin/ruby2.5')

    @parameterized.expand([
        ("ruby2.5", "/usr/bin/ruby2.5"),
    ])
    def test_supported_runtimes(self, runtime, runtime_path):
        validator = RubyRuntimeValidator(runtime=runtime, runtime_path=runtime_path)
        self.assertTrue(validator.has_runtime())

    def test_runtime_validate_unsupported_language_fail_open(self):
        validator = RubyRuntimeValidator(runtime='ruby2.4', runtime_path='/usr/bin/ruby2.4')
        validator.validate_runtime()

    def test_runtime_validate_supported_version_runtime(self):
        with mock.patch('subprocess.Popen') as mock_subprocess:
            mock_subprocess.return_value = MockSubProcess(0)
            self.validator.validate_runtime()
            self.assertTrue(mock_subprocess.call_count, 1)

    def test_runtime_validate_mismatch_version_runtime(self):
        with mock.patch('subprocess.Popen') as mock_subprocess:
            mock_subprocess.return_value = MockSubProcess(1)
            with self.assertRaises(MisMatchRuntimeError):
                self.validator.validate_runtime()
                self.assertTrue(mock_subprocess.call_count, 1)

    def test_python_command(self):
        cmd = self.validator._validate_ruby(self.validator.runtime_path)
        version_strings = [".match(2.5)"]
        for version_string in version_strings:
            self.assertTrue(all([part for part in cmd if version_string in part]))