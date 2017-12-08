# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging
from multiprocessing import Queue

from fossor.reports.report import Report


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_create_box_seperator():
    r = Report()
    for width in range(10, 21):
        result = r._create_box_seperator(width=width)
        assert '+' in result
        assert '-' in result
        assert len(result) == width


def test_create_box_middle():
    r = Report()

    for text in ['foo', 'foo' * 100]:
        for width in range(20, 41):
            result = r._create_box_middle(text=text, width=width)
            result = result
            assert 'foo' in result
            assert len(max(result.splitlines())) == width


def test_create_box():
    r = Report()
    for width in range(20, 41):
        result = r._create_box(text='foo', width=width)
        result = result.splitlines()
        assert '+' in result[0]
        assert '-' in result[0]
        assert '+' in result[-1]
        assert '-' in result[-1]
        assert 'foo' in result[1]


def test_create_generic_report():
    r = Report()
    for width in range(20, 41):
        input_queue = Queue()
        input_queue.put(('foo1', 'foobar1'))
        input_queue.put(('foo2', 'foobar2'))
        input_queue.put(('EOF', 'EOF'))

        result = r.create_report_text(input_queue, timeout=30, width=width)
        log.debug("result is:\n{0}".format(result))
        result = result.splitlines()
        assert '-' in result[0]
        assert len(result[0]) == width
        assert 'Report' in result[1]
        assert len(result[1]) == width
        assert '-' in result[2]
        assert 'Plugin: foo1' in result[3]
        assert '-' in result[4]
        assert 'foobar1' in result[5]
        assert '-' in result[6]
        assert 'Plugin: foo2' in result[7]
        assert '-' in result[8]
        assert 'foobar2' in result[9]
        assert '-' in result[10]
        assert len(result) == 11


def test_truncation():
    r = Report()
    for width in range(5, 50):
        for height in range(5, 20):
            log.debug(f"Width: {width}. Height: {height}")
            line = "1" * 30
            for y in range(10):
                text = "\n".join([line, line])
            truncated_line = r._truncate(text=text, max_width=width, max_height=height)
            truncated_line_split = truncated_line.splitlines()
            truncated_line_split = [x for x in truncated_line_split if 'Truncated' not in x]  # Remove the this line was Truncated messages from the results.
            for line in truncated_line_split:
                assert len(line) <= width
            assert len(truncated_line_split) <= height
