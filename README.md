# Fossor [![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause) [![Build Status](https://travis-ci.org/linkedin/fossor.svg?branch=master)](https://travis-ci.org/linkedin/fossor) [![Coverage Status](https://coveralls.io/repos/github/linkedin/fossor/badge.svg?branch=master)](https://coveralls.io/github/linkedin/fossor?branch=master) [![Gitter chat](https://badges.gitter.im/linkedinfossor/Lobby.png)](https://gitter.im/linkedinfossor/Lobby)
<div style="float:right;"><img src="https://github.com/linkedin/fossor/raw/master/fossor_logo.jpg" width="400" align="right"/><div style="text-align:center;padding:5px;">Fossor is "one who digs" in Latin.</div></div>
A plugin oriented tool for automating the investigation of broken hosts and services.

## Why?
Many of the initial troubleshooting tasks humans perform during an oncall escalation are the same between escalations. Fossor is a tool for automating these investigation steps. Common investigation steps can be placed into plugins that then report back to the user if they have unexpected output when Fossor is run. Unlike humans which perform tasks in serial, Fossor runs its plugins in parallel as separate processes. Output is streamed back asynchronously to the user for immediate interpretation as each plugin finishes.
### Examples of common investigative tasks:
Checking for:
- New errors in a process's logs
- New dmesg messages
- Recent network interface errors
- Recent surges in system log volume
- Memory fragmentation.
- High disk utilization
- High memory usage
- High Load averages
- High thread count
- RAID status

## Quick Start
To start using Fossor immediately with the generic built in plugins, install it using the instructions below. Then run `fossor`, optionally providing a pid if you're interested in a specific process.
```
fossor -p <pid>
```
If you have additional plugins, place them in `/opt/fossor/`. By default Fossor will run any plugins found in this location.

### Install Requirements
Fossor has the following requirements:
- Python 3.6 or higher
- python-devel packages

#### Red Hat / CentOS
These instructions were tested on CentOS 7.
```bash
sudo yum update
sudo yum install yum-utils
sudo yum groupinstall development
sudo yum install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum install python36u
sudo yum install python36u-pip
sudo yum install python36u-devel
```

#### Ubuntu 17.10
Install tested against Ubuntu 17.10, which includes a Python 3.6 system installation.

```bash
sudo apt-get install python3-dev
sudo apt-get install python3-venv
sudo apt-get install gcc
pip install --upgrade pip wheel # or install these updates into your virtualenv
```

### Install Fossor
Once the requirements from above are installed, install Fossor using one of the commands below:
##### Install system-wide
```bash
sudo pip3.6 install fossor
```
##### Install for a specific user
```bash
pip3.6 install fossor --user
```

## How does it work?
There are three types of plugins that Fossor runs in this order: `variable plugins -> check plugins -> report plugins`.
### Variable Plugins
Variable plugins are used to gather information for Check plugins. They are optional, and useful for when multiple check plugins need to gather the same information. An example of a variable plugin would be retrieving the hostname.
### Check Plugins
Check plugins perform a single investigation task. If something interesting is found, the plugin will return a string indicating this should be included in the report.
### Report Plugins
Report plugins format the data from the check plugins. This defaults to stdout. Specifying additional reports will cause those to be generated using that plugin as well.

## Contributing Code
### Adding your own plugins
Several ways to use your own plugins with Fossor

1. Add them as public Generic Plugins
   - If the plugin is generic and would be helpful to others, contribute the plugin to the Fossor project. See [Contribution guidelines for this project](CONTRIBUTING.md)
2. Add custom plugins to a local directory
   - Add your custom plugin to your `/opt/fossor` directory. By default Fossor checks and runs plugins from this location, this can be overridden via CLI flags.
3. Build and wrap Fossor
   - Fossor is both a CLI and a Python library. Import the Fossor engine into your own tool, and add any local plugins you've made by passing a module or a filesystem path to add_plugins().
   ```python
    from fossor.engine import Fossor
    from fossor.cli import main

    @fossor_cli_flags
    def main(context, **kwargs):
        f = Fossor()

        f.run(**kwargs)
   ```

### Example Plugins
Creating plugins is simple. By default, if a plugin returns a value then it's output is interesting and will be included in the report.
#### Example Variable Plugin
```python
from fossor.variables.variable import Variable

class ExampleVariable(Variable):
    def run(self, variables):
        '''If a string is returned from this method, it will be saved as a variable'''
        if 'Debug' not in variables:
            return
        if variables['Debug'] is True:
            self.log.debug("Logging example")
            return "This is an example variable that only returns when Debug is True."
```
#### Example Check Plugin
```python
from fossor.checks.check import Check

class ExampleCheck(Check):

    def run(self, variables):
        '''If a string is returned from this method, it will be reported as "interesting" output for this plugin'''
        if 'Debug' not in variables:
            return
        if variables['Debug'] is True:
            self.log.debug("Logging example")
            return 'This is an example of a check plugin. It only prints when Debug is True.
```

## More information / FAQ
### Can I contribute a plugin that checks a specific piece of software?
Yes, as long as the software it is checking is publicly available software.
### Can my plugin break Fossor?
It's possible, but Fossor tries to prevent it by isolating each plugin in its own process. If your plugin breaks, by default it will not show up in the report unless --debug is being used. If you've found a way to break Fossor and not just your own plugin, lets patch it :).
### How do I run Fossor with a specific variable overridden?
In addition to supporting the flags listed in --help, Bender also supports a generic format for inserting variables. The format is: variablename="value". This is intended for testing only. Ideally, all you need to type when you login to a machine is "fossor", or "fossor --pid <pid>".
Example: `fossor --pid 3420 --verbose  OverrideVariableForTesting="value"`
### How do I make my plugin always emit output when --verbose is in use?
To do this override the should\_notify method. The checks/buddyinfo.py plugin has an example of this. If should\_notify is overridden, it becomes a boolean method that indicates if the normal non-verbose report should display output. This means the check can always return a string without it necessarily being "interesting".
### I still have a question not answered here
Feel free to reach out on the Fossor [Gitter channel](https://gitter.im/linkedinfossor/Lobby).
