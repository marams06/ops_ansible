#!/bin/bash

cur_dir=`pwd`
SCRIPT_PATH=$(cd $(dirname "$0") && pwd -P)
SCRIPT_FILE=$0
OPS_ANSIBLE=$(dirname "${SCRIPT_PATH}")
EXT_GIT=$(dirname "${OPS_ANSIBLE}")
OPS_ANSIBLE_BASENAME=$(basename "${OPS_ANSIBLE}")
EXT_GIT_BASENAME=$(basename "${EXT_GIT}")


echo "Trying to create project in directory: ${cur_dir}"

if [ ${cur_dir} = "${SCRIPT_PATH}" ]; then
  echo "Error: You can not execute this command from ops_ansible directory"
  exit 1
fi

if [ ${cur_dir} = "${OPS_ANSIBLE}" ]; then
  echo "Error: You can not execute this command from ops_ansible directory"
  exit 1
fi

if [ -d ${cur_dir}/.git ]; then

  touch readme.rst
  mkdir -p ansible
  mkdir -p apps
  mkdir -p build
  mkdir -p command/env
  mkdir -p docs
  mkdir -p environs
  mkdir -p ext_git
  mkdir -p formulas
  mkdir -p jenkins
  mkdir -p logs
  mkdir -p playbooks
  mkdir -p scripts
  mkdir -p states
  mkdir -p validation

  touch states/readme.rst
  touch environs/readme.rst
  touch commands/readme.rst
  touch apps/readme.rst
  touch docs/readme.rst
  touch validation/readme.rst
  touch scripts/readme.rst
  touch playbooks/readme.rst

  git add .
  git commit -a -m "Devops project structure created"
  git push

else
  echo "This does not look to be an git controlled repository"
  exit 1
fi

if [ -d ${cur_dir}/ext_git ]; then

    if [ ! -d ${cur_dir}/ext_git/exbase ]; then
      git subtree add --prefix  ext_git/exbase git@github.pie.apple.com:amlgroup/exbase.git master --squash
    fi

    if [ ! -d ${cur_dir}/ext_git/ops_ansible ]; then
      git subtree add --prefix  ext_git/ops_ansible git@github.pie.apple.com:amlgroup/ops_ansible.git master --squash
    fi

    if [ ! -d ${cur_dir}/ext_git/ops_invoke ]; then
      git subtree add --prefix  ext_git/ops_invoke git@github.pie.apple.com:amlgroup/ops_invoke.git master --squash
    fi

fi

echo "Project structure created in directory: ${cur_dir}"
