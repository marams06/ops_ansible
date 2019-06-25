# AML Common Ansible framework

This project simplifies using ansible with salt projects through command line functions and some conventions.

It provides a set of common playbooks to setup devops environment, saltstack and other minor utilities. It also provides support for executing project specific playbooks defined in project's playbook directory.

## Integrating with salt project

### git setup

This has been designed to be included as a subtree of devops project git repo.

```bash
git clone git@github.pie.apple.com:amlgroup/your_project.git
cd your_project
git subtree add --prefix ext_git/ops_ansible git@github.pie.apple.com:amlgroup/ops_ansible.git master --squash
git push
```

You can then subsequently update your project with latest ops_ansible with

```bash
cd <your_project>
git subtree pull --prefix ext_git/c git@github.pie.apple.com:amlgroup/ops_ansible.git master --squash
git push
```

or

```bash
cd <your_project>
sh ext_git/ops_ansible/update_subtree.sh
git push
```

### Prequisites

Make sure ``tty requirement`` is good on the remote host.

```bash
sudo -k -l
requiretty, ...., !requiretty
```

SSH config should be configured if you use bastion host (``~/.ssh/config``).

```config
Host rn2-amlp-ladmin02.rno.apple.com
    ForwardAgent yes
    User exxxxxx
    ControlPath ~/.ssh/cm-%r@%h:%p

Host rn2-lampp-lapp*
    User exxxxxx
    ProxyCommand ssh exxxxxx@rn2-amlp-ladmin02.rno.apple.com -W %h:%p
    ServerAliveInterval 60
```

Install all ops_ansible requirements

```bash
virtualenv .venv
pip install -r ext_git/ops_ansible/requirements.txt
source .venv/bin/activate
```

### Support new environment/cluster for a project

All salt project code contains environment specific information in a subdirectory of **environs**:

```
├── environs
│   ├── prn
│   │   ├── ansible
│   │   ├── deployenv
│   │   ├── nodeconf
│   │   ├── pillar
│   │   ├── saltconf
│   │   └── statesconf
```

You need to create an ansible directory which contains inventory lists and inventory group specific variables.

```
environs/prod
├── ansible
│   ├── group_vars
│   │   ├── all
│   │   ├── decommissioned
│   │   └── osupgrade
│   ├── hadoop_racks.cfg
│   └── inventory.cfg
│   └── inventory_2.cfg
│   └── inventory_3.cfg
```
And saltconf directory that contains information required to bootstrap saltstack and nodegroup supports saltstack host groups.

```
├── nodeconf
│   └── nodegroups.conf
├── saltconf
│   ├── bootstrap.yaml
│   ├── bootstrap_python_packages.yaml
│   └── master_pub_key_file
```

In an inventory file, specify hostgroups

```config
[saltmaster]
cn2-lampp-lapp7007.asia.apple.com
[testnode]
cn2-lampp-lapp7001.asia.apple.com
```

Group specific properties are specified as yaml properties
```yaml
PROJECT_ENV: prod
is_saltmaster: false

ansible_result_email_address: aml-lamp-devops@group.apple.com
ansible_result_from_email_address: aml-lamp-devops@group.apple.com
```

Check examples directory for **bootstrap.yaml** and **bootstrap_python_packages.yaml** and group properties files.

## Using CLI

Source the environment to make CLI available

```bash
source ext_git/ops_ansible/profile/profile
```

Following commands are available.

```
execute-ansible-help                Prints this help
execute-ansible-playbook            Runs playbooks
execute-ansible-module              Runs ansible module commands
execute-ansible-ping                Runs ansible ping command
execute-csshx                       Runs csshX with a directly of hosts using host pattern
```

### execute-ansible-playbook

**Follow the command line completion tab to make it easy to include options**:

* The first option is to choose from
    *  --common for selecting common playbooks.
    * --project for selecting project specific playbooks

* Next option is to choose a salt cluster environment using
    * --environment <prod>

* Then we chose an inventory file to work with
    * --inventory <inventory.cfg>

* Other important options that are required includes

    * --ansiblehosts : to choose the host/host groups to limit the playbook action to
    * --playbook : choose a playbook to run
    * --sudoid
    * --unixid

Example:

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg --sudoid lampp --unixid exxxx --ansiblehosts saltmaster --playbook amlbin_bootstrap_user_rpms.yml
```

## Bootstrap saltstack

### Pre-requisites

Note: only required for new environment setup

Fetch the current gpg keys from existing environment saltmaster:

```bash
execute-ansible-playbook --common --environment prod --inventory inventory.cfg --sudoid lampp --unixid exxxx --playbook saltmaster_download_gpg_configs.yml --ansiblehosts saltmaster
```

Update the downloaded gpg keys to the new environment saltmaster

```bash

execute-ansible-playbook --common --environment cn --inventory inventory.cfg --sudoid lampp --unixid exxxx --playbook saltmaster_update_gpg_configs.yml --ansiblehosts saltmaster
```

### common procedures on all hosts

Install rpms specified in bootstrap configuration

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_bootstrap_user_rpms.yml --ansiblehosts <somehost>
```

Install python wheels for saltstack

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_bootstrap_python_packages.yml --ansiblehosts <somehost>
```

Update amlbin profile

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_bootstrap_setup_profile.yml --ansiblehosts <somehost>
```

### Bootstrap salt master

Generate master configuration

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_generate_master_configuration.yml --ansiblehosts <somehost>
```

### Bootstrap salt minion

Generate minion configuration on other hosts

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_generate_minion_configuration.yml --ansiblehosts <somehost>
```

Start and add salt minion

```bash
execute-ansible-playbook --common --environment cn --inventory inventory.cfg  --sudoid lampp --unixid exxxx --playbook amlbin_add_salt_minion.yml --ansiblehosts <somehost>
```

## Writing playbooks

For common playbooks, create them in c and for project playbooks, create them in <salt_project>/playbooks.

### Step 1: Create new playbook

Create a new playbook: ops_ansible/common_playbooks/test_playbook.yaml with following contents that invokes different roles:

```yaml
- hosts: all
  serial: 10
  gather_facts: yes
  ignore_errors: yes
  any_errors_fatal: false
  max_fail_percentage: 100
  vars:
      project_env: "{{ lookup('env','ANSIBLE_PROJECT_ENV') }}"
      bootstrap_definition_file: "{{ SALT_PROJECT_GIT_PATH }}/environs/{{ ANSIBLE_PROJECT_ENV }}/saltconf/bootstrap.yaml"
  roles:
    - { role: validate_amlbin , when: (validation_ansible.amlbin == True)}
    - { role: validate_disks , when: (validation_ansible.disks == True)}
    - { role: validate_mount , when: (validation_ansible.mount == True)}
```

### Step 2: Create specified role

```
├── common_playbooks
│   ├── roles
│   │   ├── amlbin_generate_minion_configuration
│   │   │   ├── tasks
│   │   │   │   └── main.yaml
│   │   │   └── templates
│   │   │       ├── minion.d
│   │   │       │   ├── directory.conf.j2
│   │   │       │   ├── grains.conf.j2
│   │   ├── validate_kernel_boot_param
│   │   │   └── tasks
│   │   │       ├── check_kernel_boot_param.yml
│   │   │       └── main.yml

```

and main.yml file should drive all specific actions

```yaml
- include_tasks: clean_local.yml
- include_tasks: archive.yml
....
```

a task like clean_local.yml contains the task

```yaml

- name: Cleanup temp directory
  file: path={{ SALT_PROJECT_GIT_PATH }}/temp state=absent
  become: no
  run_once: true
  delegate_to: localhost
  changed_when: false

- name: Create temp directory
  file: path={{ SALT_PROJECT_GIT_PATH }}/temp state=directory
  become: no
  run_once: true
  delegate_to: localhost
  changed_when: false

```
