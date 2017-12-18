# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import logging
import os
import psutil
import time

from threading import Thread
from datetime import datetime

log = logging.getLogger(__name__)

psutil_exceptions = (ProcessLookupError, PermissionError, psutil.AccessDenied, psutil.ZombieProcess, psutil.NoSuchProcess)


def comparetimerange(t, start_time, end_time) -> int:
    '''Returns 0 if within the time range, returns 1 if after the time range, returns -1 if before the time range'''
    def _convert_to_timestamp(t):
        if type(t) == str:
            t = float(t)
        elif type(t) == datetime:
            t = t.timestamp()
        return t

    if t is None:
        return None

    t = _convert_to_timestamp(t)

    if start_time:
        start_time = _convert_to_timestamp(start_time)
        if not start_time <= t:
            return -1
    if end_time:
        end_time = _convert_to_timestamp(end_time)
        if not t <= end_time:
            return 1

    return 0


def iswithintimerange(t, start_time, end_time):
    result = comparetimerange(t=t, start_time=start_time, end_time=end_time)
    if result is None:
        return None
    elif result == 0:
        return True
    return False


def get_subprocess_names():
    '''Return a list of subprocesses for the current pid'''
    current_process = psutil.Process()

    try:
        children_processes = current_process.children(recursive=True)
    except psutil_exceptions:
        pass

    children = []
    for child in children_processes:
        try:
            children.append(child.name())
        except psutil_exceptions:
            pass
    children.reverse()
    return children


class StatusPrinter(object):
    '''Continually prints the status until stopped.'''
    def __init__(self, timeout, max_width=None):
        self.start_time = time.time()
        self.timeout = timeout
        self.should_stop = False
        self.t = None
        self.line = ''
        self.max_width = 100
        if max_width:
            self.max_width = max_width

    def stop(self):
        self.should_stop = True
        if self.t:
            self.t.join()
        self.t = None

    def start(self):
        if not sys.stdout.isatty():
            return
        self.should_stop = False
        self.t = Thread(target=self.printer, args=())
        self.t.start()

    def printer(self):
        while not self.should_stop:
            time.sleep(.1)
            plugins = ', '.join({x for x in get_subprocess_names()})
            elapsed_time = int(time.time() - self.start_time)
            new_line = f"Time: {elapsed_time}/{self.timeout}. Running plugins: {plugins}"
            new_line = f"{new_line:.{self.max_width}}"
            if new_line == self.line:
                continue
            else:
                self.line = new_line

            # Clear line and return cursor to the beginning
            sys.stdout.write('\x1b[2K\r')  # Clear line and return cursor to the beginning
            sys.stdout.flush()

            # Write new line
            sys.stdout.write(self.line)
            sys.stdout.flush()

        # Do a final flush
        sys.stdout.write('\x1b[2K\r')
        sys.stdout.flush()


def get_traceback_variables():
    '''Intended to be called in the except step of a try/except clause to gather all the local variables for printing.'''
    exc_type, exc_value, tb = sys.exc_info()
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back
    output = []
    output.append("Printing variables by code frame, printing innermost code frame first.")
    for frame in stack:
        output.append("---Variables for frame {0} in {1} at line {2}---".format(frame.f_code.co_name, frame.f_code.co_filename, frame.f_lineno))
        for key, value in frame.f_locals.items():
            # Try / excepting because we have *no* idea what objects / variables str() is about to be called on.
            line = '{key}: {value}'
            try:
                key = str(key)
            except Exception as e:
                key = f'<ERROR PRINTING KEY, Exception: {e}>'
            try:
                value = str(value)
            except Exception as e:
                value = f'<ERROR PRINTING VALUE, Exception: {e}>'
            line = line.format(key=key, value=value)
            output.append(line)
    return '\n'.join(output)


def common_path(binaries):
    '''Returns the first file that os.path.isfile() from the supplied list of binaries. If none
    of the supplied list of files exist, a FileNoteFoundError is raised.'''

    for filename in binaries:
        if os.path.isfile(filename):
            return filename
    raise FileNotFoundError(', '.join(binaries))
