#!/bin/bash

cur_dir=`pwd`
SCRIPT_PATH=$(cd $(dirname "$0") && pwd -P)
SCRIPT_FILE=$0
EXT_GIT=$(dirname "${SCRIPT_PATH}")
PROJECT_GIT=$(dirname "${EXT_GIT}")

if [ -d ${PROJECT_GIT}/.git ]; then
  if [ -d ${PROJECT_GIT}/ext_git ]; then
    if [ -d ${PROJECT_GIT}/ext_git/ops_ansible ]; then
      cd $PROJECT_GIT
      git subtree pull --prefix ext_git/ops_ansible git@github.pie.apple.com:amlgroup/ops_ansible.git master --squash
      cd $cur_dir
    fi
  fi
fi
