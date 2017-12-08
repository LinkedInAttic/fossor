import os
import sys
import logging
import inspect

import fossor
from fossor.engine import Fossor


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


def test_no_popen_usage():
    f = Fossor()
    for plugin in f.list_plugins():
        for line in inspect.getsourcelines(plugin)[0]:
            print(line)
            if 'popen' in line:
                log.error("os.popen is deprecated as of python 2.6, please use the plugin.py shell_call method instead.")
                log.error('os.popen usage located in {plugin} for line {line}'.format(plugin=plugin, line=line))
            assert 'popen' not in line


def test_has_license():
    fossor_path = fossor.__path__[0]
    test_path = fossor_path + '/../test'
    paths = [fossor_path, test_path]
    for path in paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file == '__init__.py':
                    continue
                if os.path.splitext(file)[-1] != '.py':
                    continue
                filepath = os.path.join(root, file)

                has_license = False
                license = 'BSD-2 Clause license'
                with open(filepath, 'rt') as f:
                    for line in f:
                        if license in line:
                            has_license = True
                            break
                if not has_license:
                    raise Exception(f"File: {filepath} does not have the license: {license}")
