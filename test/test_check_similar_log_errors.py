# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging
import tempfile
import random
import string

from fossor.checks.similar_log_errors import SimilarLogErrors

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)

example_file_text = '''
java.util.concurrent.TimeoutException
2017/10/10 00:00:34.251 ERROR [ModelResolverOperator] [stuff] [service-foo] [543245] Some example message 1.
2017/10/10 00:00:34.251 INFO [ModelResolverOperator] [stuff] [service-foo] [145234] Some example message 2.
2017/10/10 00:04:34.251 ERROR [ModelResolverOperator] [stuff] [service-foo] [983453] Some example message 3.
2017/10/10 00:07:34.251 INFO [ModelResolverOperator] [stuff] [service-foo] [095463] Some example message 4.
2017/10/10 00:15:34.251 INFO [ComponentFoobar] [stuff] [service-bar] [242349] A substantially different set of text
'''


def test_process_line():
    sle = SimilarLogErrors()
    line = 'java.util.concurrent.TimeoutException'
    processed_line, date = sle._process_line(line=line)
    assert processed_line == line

    line = '2017/10/10 00:00:34.251 ERROR [ModelResolverOperator] [stuff] [ranker-jymbii] [random_treeid] Some message text.'
    processed_line, date = sle._process_line(line=line)
    assert processed_line == ' '.join(line.split()[2:])  # Two lines should match with the datetime stripped out

    line = '2017/10/10 00:00:34.251 INFO [ModelResolverOperator] [stuff] [ranker-jymbii] [random_treeid] Some message text.'
    processed_line, date = sle._process_line(line=line)
    assert processed_line is None  # Should be None because INFO was passed in

    line = '        at sun.reflect.GeneratedMethodAccessor67.invoke(Unknown Source) ~[?:?]'
    processed_line, date = sle._process_line(line=line)
    assert processed_line is None


def create_tmp_log_file(text, dir_path):
    path = tempfile.mktemp(dir=dir_path)
    f = open(path, 'w')
    f.write(text)
    f.close()
    return path


def test_basic_output():
    sle = SimilarLogErrors()
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = create_tmp_log_file(text=example_file_text, dir_path=tmpdir)
        variables = {}
        variables['LogFiles'] = [filepath]
        result = sle.run(variables)
    print(f"Result:\n{result}")

    assert 'filename' in result
    assert 'Count' in result
    assert 'ERROR' in result
    assert 'First seen: 2017/10/10 00:00:34.251' in result


def test_max_unique_lines():
    sle = SimilarLogErrors()

    # Create random log lines
    max_lines = sle.MAX_COMMON_LINES
    log_text = ''
    for i in range(max_lines+5):
        # random_words = [''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) for i in range(40)]  # Generate 40 5 character words
        random_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) * 50
        log_text += f'2017/10/10 00:00:34.251 ERROR {random_text}\n'

    # Confirm max_lines is honored properly
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = create_tmp_log_file(text=log_text, dir_path=tmpdir)
        variables = {}
        variables['LogFiles'] = [filepath]
        result = sle.run(variables)
    print(f"Result:\n{result}")
    assert 'Other Error Lines' in result
    assert 'Count: 5' in result
