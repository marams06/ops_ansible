

import os
import os.path
import click
import yaml
import sys
from pprint import pprint
from ConfigParser import SafeConfigParser
from unipath import Path
import socket


from ansible.utils.shlex import shlex_split
from ansible.parsing.dataloader import DataLoader
from ansible.inventory.ini import InventoryParser
from ansible.inventory.group import Group
from jinja2 import Environment

script_path = os.path.dirname(os.path.abspath(__file__))
script_dir = os.path.dirname(script_path)
exbase_dir = os.path.dirname(script_dir)
project_dir = os.path.dirname(exbase_dir)

host_template="""
{% for hostname, hostname_ip in hostnames.items() %}
{% set short_name = hostname.split('.')[0] %}
define host {
    host_name                       {{ short_name }}
    alias                           {{ hostname }}
    address                         {{ hostname_ip }}
    max_check_attempts              3
    contact_groups                  contacts-all
    min_business_impact             1
    retain_status_information       1
    retain_nonstatus_information    1
    use                             base-host
    register                        1
}
{% endfor %}
"""

def get_ipaddress(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

@click.command()
@click.option('--environment', default=None, help='Provide environment to pick inventory file: <prod>', type=str)
@click.option('--outputdir', default=None, help='relative path where output files are written')
def gen_host_definitions(environment, outputdir=None):
    """
    Generates host file suitable for icinga monitoring 

    Example:

        python generate_monitoring_host_file.py --environment prod --outputdir=
    """
    ansible_inventory_file = os.path.join(project_dir, 'environs', environment, 'ansible', 'inventory.cfg')
    loader = DataLoader()
    group_dict = {
        'all': Group(name='all'),
        'ungrouped': Group(name='ungrouped')
    }
    parser = InventoryParser(loader=loader, groups=group_dict, filename=ansible_inventory_file)
    hostname_dict = parser.hosts
    hostname_list = hostname_dict.values()
    hostnames = {}
    for hostname in hostname_list:
        x = get_ipaddress(str(hostname))
        if x: hostnames[str(hostname)] = x
    host_definition = Environment().from_string(host_template).render(hostnames=hostnames)
    project_host_cfg = Path(outputdir, 'project_hosts.cfg')
    project_host_cfg = project_host_cfg.expand()
    with open(str(project_host_cfg), 'w') as f:
        f.write(host_definition)
        f.close()
    


if __name__ == '__main__':
    gen_host_definitions()
