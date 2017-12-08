# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging

from fossor.checks.similar_log_errors import SimilarLogErrors

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_process_line():
    sle = SimilarLogErrors()
    line = 'java.util.concurrent.TimeoutException'
    assert sle._process_line(line=line) == line

    line = '2017/10/10 00:00:34.251 ERROR [ModelResolverOperator] [stuff] [ranker-jymbii] [random_treeid] Some message text.'
    result = sle._process_line(line=line)
    assert result == ' '.join(line.split()[2:])  # Two lines should match with the datetime stripped out

    line = '2017/10/10 00:00:34.251 INFO [ModelResolverOperator] [stuff] [ranker-jymbii] [random_treeid] Some message text.'
    result = sle._process_line(line=line)
    assert result is None  # Should be None because INFO was passed in

    line = '        at sun.reflect.GeneratedMethodAccessor67.invoke(Unknown Source) ~[?:?]'
    assert sle._process_line(line=line) is None


def test_grouping_similar_lines():
    sle = SimilarLogErrors()
    common_lines = {}
    common_lines['This is a line that is very distinct.'] = 2
    common_lines['The rain in spain falls mainly in the plains'] = 5
    common_lines['The quick brown fox jumps over the fence and goes to the grocery store.'] = 4

    line = 'The quick RANDOM brown fox jumps TEXT over the fence and goes to the grocery store.'
    result = sle._group_similar_log_lines(line=line, common_lines=common_lines)
    log.debug(f"result: {result}")
    assert result['The quick brown fox jumps over the fence and goes to the grocery store.'] == 5
