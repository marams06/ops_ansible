#!/usr/bin/env python

"""
Generic ansible command deployer.
"""

import click
import os
import os.path
import sys


# Import ansible environment

script_path = os.path.dirname(os.path.abspath(__file__))
print(script_path)

#if not script_path.endswith('ext_git/ops_ansible'):
#    print("This script should be called from the projects external module: ext_git/ops_ansible")
#    sys.exit(1)


@click.command()
@click.argument('hostname')
@click.argument('unix_command')
def execute_ansible_adhoc(hostname, unix_command):
    """
    Execute ansible adhoc command
    """
    pass


if __name__ == '__main__':
    execute_ansible_adhoc()
