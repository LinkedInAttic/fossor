#!/usr/bin/env python
# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.


from __future__ import absolute_import
from __future__ import print_function

import sys
import click
import logging
import setproctitle
import parsedatetime as pdt

from functools import wraps
from datetime import datetime, timedelta

from fossor.engine import Fossor

default_plugin_dir = '/opt/fossor'


def setup_logging(ctx, param, value):
    level = logging.CRITICAL
    if value:
        level = logging.DEBUG
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(stream=sys.stderr, level=level)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    return value


def get_timestamp(value):
    '''Return timestamp from a human readable date'''

    if not value:
        return

    # If already a timestamp return a float
    try:
        timestamp = float(value)
        return timestamp
    except ValueError:
        pass

    # Convert human readable string to timestamp
    cal = pdt.Calendar()
    timestamp = (cal.parseDT(value)[0]).timestamp()
    return timestamp


def set_start_time(ctx, param, value):
    if 'start_time' in ctx.params and ctx.params['start_time'] is not None:
        return ctx.params['start_time']
    return get_timestamp(value)


def set_end_time(ctx, param, value):
    return get_timestamp(value)


def set_relative_start_time(ctx, param, value):
    '''Overrides start time relative to number of {value} hours'''
    hours = value

    start_time = (datetime.now() - timedelta(hours=hours)).timestamp()
    ctx.params['start_time'] = start_time


class CsvList(click.ParamType):
    name = 'Csv-List'

    def convert(self, value, param, ctx):
        result = value.split(',')
        return result


def fossor_cli_flags(f):
    '''Add default Fossor CLI flags'''
    # Flags will appear in reverse order of how they  are listed here:
    f = add_dynamic_args(f)  # Must be applied after all other click options since this requires click's context object to be passed

    # Add normal flags
    csv_list = CsvList()
    f = click.option('--black-list', 'blacklist', type=csv_list, help='Do not run these plugins.')(f)
    f = click.option('--white-list', 'whitelist', type=csv_list, help='Only run these plugins.')(f)
    f = click.option('--truncate/--no-truncate', 'truncate', show_default=True, default=True, is_flag=True)(f)
    f = click.option('-v', '--verbose', is_flag=True)(f)
    f = click.option('-d', '--debug', is_flag=True, callback=setup_logging)(f)
    f = click.option('-t', '--time-out', 'timeout', show_default=True, default=600, help='Default timeout for plugins.')(f)
    f = click.option('--end-time', callback=set_end_time, help='Plugins may optionally implement and use this. Defaults to now.')(f)
    f = click.option('--start-time', callback=set_start_time, help='Plugins may optionally implement and use this.')(f)
    f = click.option('-r', '--report', type=click.STRING, show_default=True, default='StdOut', help='Report Plugin to run.')(f)
    f = click.option('--hours', type=click.INT, default=24, show_default=True, callback=set_relative_start_time,
                     help='Sets start-time to X hours ago. Plugins may optionally implement and use this.')(f)
    f = click.option('--plugin-dir', default=default_plugin_dir, show_default=True, help=f'Import all plugins from this directory.')(f)
    f = click.option('-p', '--pid', type=click.INT, help='Pid to investigate.')(f)

    # Required for parsing dynamics arguments
    f = click.pass_context(f)
    f = click.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=['-h', '--help']))(f)
    return f


def add_dynamic_args(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        context = args[0]
        dynamic_kwargs = parse_dynamic_args(context.args)
        kwargs = {**kwargs, **dynamic_kwargs}  # Merge these dict objects
        function(*args, **kwargs)
    return wrapper


def set_process_title(arg=None):
    '''
    Decorator for setting the process title
    Can be applied in two ways:
    @set_process_title
    @set_process_title('new_process_title')

    Defaults to 'fossor'

    '''
    title = 'fossor'
    if type(arg) == str:
        title = arg

    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            setproctitle.setproctitle(title + ' ' + ' '.join(sys.argv[1:]))
            function(*args, **kwargs)
        return wrapper
    # If called as @set_process_title
    if callable(arg):
        return real_decorator(arg)
    # If called as @set_process_title('new_title')
    return real_decorator


@fossor_cli_flags
@set_process_title
def main(context, **kwargs):
    """Fossor is a plugin oriented tool for automating the investigation of broken hosts and services.

    \b
    Advanced:
    Multiple additional internal variables may be passed on the command line in this format: name="value".
    This is intended for testing or automation.
    """  # \b makes click library honor paragraphs

    f = Fossor()
    f.run(**kwargs)


def parse_dynamic_args(context_args):
    '''Return a dict of arguments with their values. Intended to parse leftover arguments from click's context.arg list'''
    log = logging.getLogger(__name__)
    log.debug(f"Remaining Arguments that will be used for dynamic args now that hardcoded cli flags have been removed: {context_args}")
    format_help_message = "Please use --help to see valid flags. Or use the name=value method for setting internal variables."

    kwargs = {}
    for arg in context_args:
        a = arg.strip()
        if a.startswith('-'):
            raise ValueError(f"Argument: {arg} is invalid {format_help_message}.")
        try:
            name, value = a.split('=')
            kwargs[name] = value
            log.debug(f"Using dynamic variable {name}={value}")
        except Exception as e:
            log.exception(f"Failed to add argument: \"{arg}\". {format_help_message} Exception was: {e}")
            raise e
    return kwargs


if __name__ == '__main__':
    main()
