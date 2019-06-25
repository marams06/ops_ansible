#!/usr/bin/env python
#
# Generate csshX inventory
#

import os
import os.path
import sys
import argparse
import errno

from ansible.parsing.dataloader import DataLoader
from ansible.inventory.manager import InventoryManager


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def generate_csshx_inventory(ansible_inventory, csshx_inventory):
    data_loader = DataLoader()
    inventory = InventoryManager(loader=data_loader,
                                 sources=[ansible_inventory])
    groups_dict = inventory.get_groups_dict()
    clusters = []
    group_inventory = []
    for group_key, group_items in groups_dict.items():
        if group_items:
            group_key_normalized = group_key.encode('ascii', 'ignore')
            clusters.append(group_key_normalized)
            group_items_normalized = [
                x.encode('ascii', 'ignore') for x in group_items]
            group_items_string = " ".join(group_items_normalized)
            inventory_string = "%s = %s" % (
                group_key_normalized, group_items_string)
            group_inventory.append(inventory_string)
    if clusters:
        cluster_names = " ".join(clusters)
        cluster_string = "clusters = %s" % cluster_names
        with open(csshx_inventory, 'w') as f:
            f.write("%s\n" % cluster_string)
            for line in group_inventory:
                f.write("%s\n" % line)
            f.close()


def main():
    text = 'gen_csshx_inventory.py generates csshX configuration'
    parser = argparse.ArgumentParser(prog='gen_csshx_inventory.py',
                                     description=text)
    parser_behaviour = parser.add_argument_group('mandatory')
    parser_behaviour.add_argument(
        "--input", "-i", help="path to ansible inventory file")
    parser_behaviour.add_argument(
        "--output", "-o", help="path to csshX inventory file")
    args = parser.parse_args()
    if args.input is None:
        print("No ansible inventory was provided")
        sys.exit(1)
    elif not os.path.exists(args.input):
        print("Ansible inventory provided does not exist: %s" % args.input)
        sys.exit(1)
    if args.output is None:
        print("No csshX inventory output file was provided")
        sys.exit(1)
    input_dir = os.path.dirname(args.input)
    mkdir_p(input_dir)
    generate_csshx_inventory(args.input, args.output)


if __name__ == '__main__':
    main()
