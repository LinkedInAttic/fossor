# Fossor
<div style="float:right;"><img src="https://github.com/linkedin/fossor/raw/master/fossor_logo.jpg" width="400" align="right"/><div style="text-align:center;padding:5px;">Fossor is "one who digs" in Latin.</div></div>
A plugin oriented tool for automating the investigation of broken hosts and services.

## Why?
When someone is oncall, many of the initial troubleshooting tasks humans perform during an escalation are the same between escalations. Fossor is a tool for automating these investigation steps. Common investigation steps can be placed into plugins that then report back to the user if they have unexpected output when Fossor is run. Unlike humans which perform tasks in serial, Fossor runs its plugins in parallel as separate processes. Output is streamed back asynchronously to the user for immediate interpretation as plugins finish.
### Examples of common tasks:
- Checking for recent dmesg messages
- Checking that the disk is not full
- Checking for garbage collection problems
- Checking for high memory usage
- Checking network interface errors
- Checking for downstreams latency
- Checking for memory fragmentation.
- Checking for unbalanced numa nodes
- Checking for RAID status

## Quick Start
To start using Fossor immediately with the generic built in plugins, ensure python 3.6+ is installed. Then use pip3 to install Fossor and run it, optionally providing a pid if you're interested in a specific process:
```
pip3 install fossor
fossor -p <pid>
```
If you have additional plugins, place them in `/opt/fossor/`. By default Fossor will run any plugins found in this location.

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
   - Fossor is both a CLI and a Python library. Import the Fossor engine into your own tool, and add any local plugins you've made via an import.

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
### How do I run Fossor with a specific variable arbitrarily overridden?
In addition to supporting the flags listed in --help, Bender also supports a generic format for inserting variables. The format is: variablename="value". This is intended for testing only. Ideally, all you need to type when you login to a machine is "fossor", or "fossor --pid <pid>".
Example: `fossor --pid 3420 --verbose  OverrideVariableForTesting="value"`
### How do I make my plugin always emit output when --verbose is in use?
To do this override the should\_notify method. The checks/buddyinfo.py plugin has an example of this. If should\_notify is overridden, it becomes a boolean method that indicates if the normal non-verbose report should display output. This means the check can always return a string without it necessarily being "interesting".
### I still have a question not answered here
Feel free to reach out to [scallister@linkedin.com](mailto:scallister@linkedin.com)
