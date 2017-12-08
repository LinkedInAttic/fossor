# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging

from fossor.cli import main
from click.testing import CliRunner

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_fossor_help_menu():
    runner = CliRunner()
    result = runner.invoke(main, args=['-h', '--timeout 1'])
    assert result.exit_code == 0
    assert 'Usage' in result.output
    assert '--help' in result.output


def test_fossor_extra_kwarg():
    runner = CliRunner()
    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', 'foo=2', '--verbose', '--no-truncate'])
    assert result.exit_code == 0
    assert 'foobar=5' in result.output
    assert 'foo=2' in result.output


def test_fossor_invalid_kwarg():
    runner = CliRunner()
    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', '--not-a-valid-flag'])
    assert result.exit_code == -1
    assert '' == result.output

    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', '--another-invalid-flag'])
    assert result.exit_code == -1
    assert '' == result.output

    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', '6'])
    assert result.exit_code == -1
    assert '' == result.output

    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', '--another-invalid-flag', '6'])
    assert result.exit_code == -1
    assert '' == result.output

    result = runner.invoke(main, args=['--time-out', '1', 'foobar=5', '--not-a-valid-flag', '--another-invalid-flag', '6'])
    assert result.exit_code == -1
    assert '' == result.output
