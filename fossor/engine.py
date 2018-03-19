# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import os
import time
import psutil
import signal
import logging
import importlib
import setproctitle
import inspect
import pkgutil
import multiprocessing as mp

from requests.structures import CaseInsensitiveDict

import fossor.plugin
import fossor.variables
import fossor.variables.variable
import fossor.checks
import fossor.checks.check
import fossor.reports
import fossor.reports.report

from fossor.utils.misc import psutil_exceptions


class Fossor(object):
    '''
    Engine for running automated investigations using three plugin types: variables, checks, reports. The engine:
    - Collects variables
    - Runs checks using applicable variables
    - Reports noteworthy findings
    '''
    def __init__(self):
        self.log = logging.getLogger(__name__)

        self.plugin_parent_classes = [fossor.plugin.Plugin,
                                      fossor.variables.variable.Variable,
                                      fossor.checks.check.Check,
                                      fossor.reports.report.Report]

        # Variables
        self.variables = CaseInsensitiveDict()
        self.add_variable('timeout', 600)  # Default timeout

        # Imported Plugins
        self.variable_plugins = set()
        self.check_plugins = set()
        self.report_plugins = set()

        self.add_plugins()  # Adds all plugins located within the fossor module recursively

    def _import_submodules_by_module(self, module) -> set:
        """
        Import all submodules from a module.
        Returns a set of modules
        """
        if '__path__' not in dir(module):
            return set()  # No other submodules to import, this is a file
        result = set()
        for loader, name, is_pkg in pkgutil.iter_modules(path=module.__path__):
            sub_module = importlib.import_module(module.__name__ + '.' + name)
            result.add(sub_module)
            result.update(self._import_submodules_by_module(sub_module))

        return result

    def _import_submodules_by_path(self, path: str) -> set:
        """
        Import all submodules from a path.
        Returns a set of modules
        """
        # Get a list of all the python files
        # Loop over list and group modules

        path = os.path.normpath(path)
        all_file_paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                all_file_paths.append(os.path.join(root, file))

        python_file_paths = [file for file in all_file_paths if '.py' == os.path.splitext(file)[1]]

        result = set()
        for filepath in python_file_paths:
            # Create a module_name
            relative_path = filepath.split(path)[-1]
            module_name = os.path.splitext(relative_path)[0]  # Remove file extension
            module_name = module_name.lstrip(os.path.sep)  # Removing leading slash
            module_name = module_name.replace(os.path.sep, '.')  # Change / to .
            module_name = f'fossor.local.{module_name}'

            # Import with the new name
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result.add(module)

        return result

    def add_plugins(self, source=fossor):
        '''
        Recursively return a dict of plugins (classes) that inherit from the given parent_class) from within that source.
        source accepts either a python module or a filesystem path as a string.
        '''
        if source is None:
            return

        if type(source) == str:
            modules = self._import_submodules_by_path(path=source)
        else:
            modules = self._import_submodules_by_module(source)

        for module in modules:
            for obj_name, obj in module.__dict__.items():
                # Get objects from each module that look like plugins for the Check abstract class
                if not inspect.isclass(obj):  # Must check if a class otherwise the next check with issubclass will get a TypeError
                    continue
                if obj in self.plugin_parent_classes:  # If this is one of the parent classes, skip, we only want the children
                    continue
                if issubclass(obj, fossor.variables.variable.Variable):
                    self.variable_plugins.add(obj)
                elif issubclass(obj, fossor.checks.check.Check):
                    self.check_plugins.add(obj)
                elif issubclass(obj, fossor.reports.report.Report):
                    self.report_plugins.add(obj)
                else:
                    continue
                self.log.debug(f"Adding Plugin ({obj_name}, {obj})")

    def clear_plugins(self):
        self.variable_plugins = set()
        self.check_plugins = set()
        self.report_plugins = set()

    def list_plugins(self):
        variables = list(self.variable_plugins)
        checks = list(self.check_plugins)
        reports = list(self.report_plugins)
        return variables + checks + reports

    def _terminate_process_group(self, process):
        '''Kill a process group leader and its process group'''
        pid = process.pid
        pgid = os.getpgid(pid)
        if pid != pgid:
            raise ValueError(f"Trying to terminate a pid that is not a pgid leader. pid: {pid}, pgid: {pgid}.")  # This should never happen

        # Try these signals to kill the process group
        for s in (signal.SIGTERM, signal.SIGKILL):
            try:
                children = psutil.Process().children(recursive=True)
            except psutil_exceptions:
                continue  # Process is already dead

            if len(children) > 0:
                try:
                    self.log.warning(f"Issuing signal {s} to process group {pgid} because it has run for too long.")
                    os.killpg(pgid, s)
                    time.sleep(1)
                except psutil_exceptions:
                    pass
                except PermissionError:  # Occurs if process has already exited on MacOS
                    pass
        # Terminate the plugin process (which is likely dead at this point)
        process.terminate()
        process.join()

    def _run_plugins_parallel(self, plugins):
        '''
        Accepts function to run, and a dictionary of plugins to run. Format is name:module
        Returns an output queue which outputs two values: plugin-name, output. Queue ends when plugin-name is EOF.

        '''

        def _run_plugins_parallel_helper(timeout):
            setproctitle.setproctitle('Plugin-Runner')
            processes = []
            queue_lock = mp.Lock()

            for Plugin in plugins:
                process = mp.Process(target=self.run_plugin, name=Plugin.get_name(), args=(Plugin, output_queue, queue_lock))
                process.start()
                processes.append(process)

            start_time = time.time()
            should_end = False
            while len(processes) > 0:

                time_spent = time.time() - start_time
                should_end = time_spent > timeout

                try:
                    os.kill(os.getppid(), 0)  # Check if the parent process is alive
                except ProcessLookupError:
                    should_end = True

                for process in processes:  # Using list so I can delete while iterating
                    process_is_dead = not process.is_alive() and process.exitcode is not None
                    if process_is_dead:
                        process.join()
                        processes.remove(process)
                        continue
                    if should_end:
                        with queue_lock:
                            self.log.error(f"Process {process} for plugin {process.name} ran longer than the timeout period: {timeout}")
                            if self.variables.get('verbose'):
                                output_queue.put((process.name, 'Timed out (use --time-out to increase timeout)'))
                            self._terminate_process_group(process)
                            processes.remove(process)
                time.sleep(.1)

            with queue_lock:
                output_queue.put(('Stats', f'Ran {len(plugins)} plugins.'))
                output_queue.put(('EOF', 'EOF'))  # Indicate the queue is finished

            return output_queue

        timeout = int(self.variables.get('timeout'))

        # Run plugins in parallel
        # This child process will spawn child processes for each plugin, and then do the final termination and clean-up.
        # A separate child process for spawning plugin processes is needed because only a parent process can terminate its children.
        # This allows us to continue to the reporting phase while the checks finish.
        output_queue = mp.Queue()
        parallel_plugins_helper_process = mp.Process(target=_run_plugins_parallel_helper, name='parallel_plugins_helper_process', args=(timeout, ))
        parallel_plugins_helper_process.start()

        return output_queue

    def run_plugin(self, Plugin, output_queue, queue_lock):
        try:
            os.setsid()  # Causes this plugin to become a process group leader, we can then kill that process group to kill all potential subprocesses
            p = Plugin()
            setproctitle.setproctitle(p.get_name())
            output = ''
            if p.should_run():
                output = p.run_helper(variables=self.variables)
                if output:
                    with queue_lock:  # Prevents the queue from becoming corrupt on process termination
                        output_queue.put((p.get_name(), output))
        except Exception as e:
            # This ensures that any plugins that fail to initialize show up properly in the report and don't output errors mid report.
            self.log.exception(f"Plugin {p} failed to initialize", e)

    def get_variables(self):
        '''
        Gather all possible variables that may be useful for plugins
            - Variables can have interdependencies, this will continue gathering missing variables
              until no new variables have appeared after a run
            - Can be run again if new variables are added to fill in any blanks
        '''
        while True:
            variable_count = len(self.variables)
            output_queue = self._run_plugins_parallel(self.variable_plugins)
            while True:
                name, output = output_queue.get()
                if 'EOF' in name:
                    break
                if name in self.variables:
                    self.log.debug("Skipping variable plugin because it has already been found: {vp}".format(vp=name))
                    continue
                self.add_variable(name, output)
            output_queue.close()

            if variable_count == len(self.variables):
                self.log.debug("Done finding variables: {variables}".format(variables=self.variables))
                break

    def _convert_simple_type(self, value):
        '''Convert String to simple type if possible'''
        if type(value) == str:
            if 'false' == value.lower():
                return False
            if 'true' == value.lower():
                return True
            try:
                return int(value)
            except ValueError:
                pass
            try:
                return float(value)
            except ValueError:
                pass

        return value

    def add_variables(self, **kwargs):
        for name, value in kwargs.items():
            self.add_variable(name=name, value=value)
        return True

    def add_variable(self, name, value):
        '''Adds variable, converts numbers and booleans to their types'''
        if name in self.variables:
            old_value = self.variables[name]
            if value != old_value:
                self.log.warning(f"Variable {name} with value of {old_value} is being replaced with {value}")

        value = self._convert_simple_type(value)

        self.variables[name] = value
        self.log.debug("Added variable {name} with value of {value} (type={type})".format(name=name, value=value, type=type(value)))
        return True

    def _process_whitelist(self, whitelist):
        if whitelist:
            whitelist = [name.casefold() for name in whitelist]
            self.variable_plugins = {plugin for plugin in self.variable_plugins if plugin.get_name().casefold() in whitelist}
            self.check_plugins = {plugin for plugin in self.check_plugins if plugin.get_name().casefold() in whitelist}

    def _process_blacklist(self, blacklist):
        if blacklist:
            blacklist = [name.casefold() for name in blacklist]
            self.variable_plugins = {plugin for plugin in self.variable_plugins if plugin.get_name().casefold() not in blacklist}
            self.check_plugins = {plugin for plugin in self.check_plugins if plugin.get_name().casefold() not in blacklist}

    def run(self, report='StdOut', **kwargs):
        '''Runs Fossor with the given report. Method returns a string of the report output.'''
        self.log.debug("Starting Fossor")

        self._process_whitelist(kwargs.get('whitelist'))
        self._process_blacklist(kwargs.get('blacklist'))

        # Add kwargs as variables
        self.add_variables(**kwargs)

        # Add directory plugins
        self.add_plugins(kwargs.get('plugin_dir'))

        # Gather Variables
        self.get_variables()

        # Run checks
        output_queue = self._run_plugins_parallel(self.check_plugins)

        # Run Report
        try:
            Report_Plugin = [plugin for plugin in self.report_plugins if report.lower() == plugin.get_name().lower()].pop()
        except IndexError:
            message = f"Report_Plugin: {report}, was not found. Possibly reports are: {[plugin.get_name() for plugin in self.report_plugins]}"
            self.log.critical(message)
            raise ValueError(message)

        report_plugin = Report_Plugin()
        return report_plugin.run(variables=self.variables, report_input=output_queue)
