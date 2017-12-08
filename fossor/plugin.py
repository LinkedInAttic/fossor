# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import logging
import subprocess
import io
import traceback

from fossor.utils.misc import get_traceback_variables
from abc import ABCMeta, abstractmethod


class Plugin(metaclass=ABCMeta):
    '''Super class for Variable and Check plugins'''

    def should_run(self):
        '''By default always run'''
        return True

    @classmethod
    def get_name(cls):
        return cls.__name__

    @classmethod
    def get_full_name(cls):
        return cls.__module__ + '.' + cls.get_name()

    @property
    def log(self):
        return logging.getLogger(self.get_full_name())

    def shell_call(self, cmd, stream=False):
        '''
        Cmd accept a string to run in the shell
        return_code=False

        Output:
        out (string), err (string), returncode (int)

        Output if stream=True:
        out (string stream), err (string stream), returncode (int)
        '''
        if type(cmd) == str:
            cmd = cmd.split()
        self.log.debug(f"Executing shell command: {cmd}")
        p = subprocess.Popen(cmd,
                             stderr=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             close_fds=True,
                             shell=False,
                             encoding='utf-8',
                             start_new_session=False)
        if stream:
            self.log.debug(f"Not printing output since command being streamed: {cmd}")
            return p.stdout, p.stderr, p.returncode
        out, err = p.communicate()
        self.log.debug(f"Command: {cmd}, had a stdout of: {out}")
        if err:
            self.log.warning(f"Command: {cmd}, had a stderr of: {err}")
        return out, err, p.returncode

    @abstractmethod
    def run(self, variables: dict):
        '''By default, this will only report if something is outputted.'''
        pass

    def run_helper(self, variables: dict):
        '''Helper method, tracks output for plugins that want to use run as their only method. Returns a string as output.'''
        self.error = None
        self.output = None
        self.log.debug("Starting")
        try:
            self.output = self.run(variables)
            self.log.debug("Finished")
        except Exception as e:
            with io.StringIO() as output:
                traceback.print_tb(e.__traceback__, file=output)
                output.seek(0)
                trace = output.read()
            trace_variables = get_traceback_variables()
            self.error = f"Crash Report (Execution Failed)\n---exception---\n{e}\n---traceback---\n{trace}\n---variables---\n{trace_variables}"
        if self.should_notify():
            return self.output
        if not variables.get('verbose'):
            return
        if self.error:
            self.log.debug(f"Error Report: {self.error}")
            return self.error
        if self.output:
            return self.output

    def should_notify(self):
        '''Return True if the Plugin output should be returned. Can be overridden by a subclass.'''
        if self.output:
            return True
