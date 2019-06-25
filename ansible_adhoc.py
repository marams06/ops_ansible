#!/usr/bin/env python

"""
Generic ansible command deployer.
"""

import click
import os
import os.path
import sys
import json
from pprint import pprint

from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
from ansible.utils.unicode import to_unicode

script_path = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(script_path)
project_dir = os.path.dirname(script_dir)

part_of_ext_git = True

if not script_path.endswith('ext_git/ops_ansible'):
    print("This script is not being called from the projects external module: ext_git/ops_ansible")
    part_of_ext_git = False

Options = namedtuple('Options',
                ['connection', 'module_path', 'forks', 'become',
                 'become_method', 'become_user', 'check']
            )


command_template="""
Run the following command: {unix_command}
with user: {user}
as sudo user: {sudouser}
on hosts: {hosts}
using inventory file: {inventoryfile}
"""


class ResultCallback(CallbackBase):
    """callback plugin used for performing an action as results come in.
    """
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json representation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        host = result._host
        print json.dumps({host.name: result._result}, indent=4)

class ResultsCollector(CallbackBase):
    def __init__(self, *args, **kwargs):
        super(ResultsCollector, self).__init__(*args, **kwargs)
        self.host_ok     = {}
        self.host_unreachable = {}
        self.host_failed = {}

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable[result._host.get_name()] = result

    def v2_runner_on_ok(self, result,  *args, **kwargs):
        self.host_ok[result._host.get_name()] = result

    def v2_runner_on_failed(self, result,  *args, **kwargs):
        self.host_failed[result._host.get_name()] = result


@click.command()
@click.option('--user', default=None, help='Your unix id exxxxxx', type=str)
@click.option('--sudouser', default=None, help='run the command as sudo user. example athenap')
@click.option('--hosts', default=None, help='Host on which to run ansible ad-hoc command', type=str)
@click.option('--environment', default=None, help='Provide environment to pick inventory file: <prod>', type=str)
@click.option('--hostpattern', default=None, help='Provide host pattern to run adhoc commands on', type=str)
@click.option('--unix_command', default=None, help='ad-hoc command to run on host')
@click.option('--output', default=None, help='Write json output to a file')
def execute_ansible_adhoc(user, sudouser, hosts, environment, hostpattern, unix_command, output):
    """
    Execute ansible adhoc command

    Example:

        python ansible_adhoc.py --user=exxxxx --sudouser=lampp --unix_command='uptime' --environment prod --hostpattern='rn2-lampp-lapp600*.rno.apple.com'

        python ansible_adhoc.py --user=exxxxx --sudouser=lampp --unix_command='uptime' --hosts=rn2-lampp-lapp6016.rno.apple.com

        python ansible_adhoc.py --user=exxxxx --sudouser=lampp --unix_command='uptime' --hosts='rn2-lampp-lapp6016.rno.apple.com,rn2-lampp-lapp6017.rno.apple.com'
    """
    # Input checks
    if not unix_command:
        print("Error: You have not provided the unix command to run. Check help")
        sys.exit(1)

    if not user:
        print("Error: You have not provided the user if with which to access remote server")
        sys.exit(1)


    use_hosts_list = True
    if part_of_ext_git:
        if hosts is None:
            if environment is None or hostpattern is None:
                print("Error: You have to provide hosts list or an environment for inventory file and host pattern to run commands on")
                sys.exit(1)
            else:
                use_hosts_list = False
                inventory_file = os.path.join(project_dir, 'environs', environment, 'ansible', 'inventory.cfg')
                print(command_template.format(user=user, sudouser=sudouser, hosts=hostpattern, unix_command=unix_command, inventoryfile=inventory_file))
    else:
        if hosts is None:
            print("Error: Not a part of salt repo. Please provide a comma seperated hosts list")
            sys.exit(1)
        else:
            print(command_template.format(user=user, sudouser=sudouser, hosts=hosts, unix_command=unix_command, inventoryfile=''))




    variable_manager = VariableManager()
    loader = DataLoader()
    options = None
    if not sudouser:
        options = Options(connection='ssh',
                          module_path='',
                          forks=100,
                          become=False,
                          become_method=None,
                          become_user='',
                          check=False
                          )
    else:
        options = Options(connection='ssh',
                          module_path='',
                          forks=100,
                          become=True,
                          become_method='sudo',
                          become_user=sudouser,
                          check=False
                          )
    passwords = dict(vault_pass='secret')
    inventory = None
    run_on_hosts = None
    if use_hosts_list:
        host_list = hosts.split(',')
        run_on_hosts = host_list
        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=host_list)
    else:
        inventory_file = os.path.join(project_dir, 'environs', environment, 'ansible', 'inventory.cfg')
        inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=inventory_file)
        run_on_hosts = to_unicode(hostpattern, errors='strict')

    variable_manager.set_inventory(inventory)
    results_callback = ResultsCollector()
    # create play with tasks
    play_source =  dict(
        name = "Ansible Play",
        hosts = run_on_hosts,
        gather_facts = 'no',
        tasks = [
            dict(action=dict(module='shell', args=unix_command), register='shell_out'),
            dict(action=dict(module='debug', args=dict(msg='{{shell_out.stdout}}')))
         ]
    )
    tqm = None
    try:
        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=passwords,
                stdout_callback=results_callback,
            )
        tqm._stdout_callback = results_callback
        result = tqm.run(play)
    finally:
        if tqm is not None:
            tqm.cleanup()
    results_raw = {'success': {}, 'failed': {}, 'unreachable': {}}
    for host, result in results_callback.host_ok.items():
        if result: results_raw['success'][host] =  result._result['msg']

    for host, result in results_callback.host_failed.items():
        if result: results_raw['failed'][host] = result._result['msg']

    for host, result in results_callback.host_unreachable.items():
        if result: results_raw['unreachable'][host] = result._result['msg']

    if output:
        with open(output, 'w') as f:
            results_raw_json = json.dumps(results_raw)
            f.write(results_raw_json)
            f.close()
    else:
        print("Results from all hosts:\n")
        pprint(results_raw, width=1, indent=2)




if __name__ == '__main__':
    execute_ansible_adhoc()
