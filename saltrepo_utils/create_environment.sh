#!/bin/bash

if [ -z "$1" ]; then
  echo "sh create_enviornmanet <project_env>"
  exit 1
fi

project_env=$1
cur_dir=`pwd`
SCRIPT_PATH=$(cd $(dirname "$0") && pwd -P)
SCRIPT_FILE=$0
OPS_ANSIBLE=$(dirname "${SCRIPT_PATH}")
EXT_GIT=$(dirname "${OPS_ANSIBLE}")
PROJECT_GIT=$(dirname "${EXT_GIT}")

if [ ${cur_dir} = "${SCRIPT_PATH}" ]; then
  echo "Error: You can not execute this command from ops_ansible directory"
  exit 1
fi

if [ ${cur_dir} = "${OPS_ANSIBLE}" ]; then
  echo "Error: You can not execute this command from ops_ansible directory"
  exit 1
fi

if [ -d ${PROJECT_GIT}/.git ]; then
  if [ -d ${PROJECT_GIT}/ext_git/ops_ansible ]; then
    echo "Creating environment: ${project_env}"
    if [ -d ${PROJECT_GIT}/environs/${project_env} ]; then
      echo "Project environment already exists at : ${PROJECT_GIT}/environs/${project_env}"
      exit 0
    else
      echo "Creating project environment at : ${PROJECT_GIT}/environs/${project_env}"
      mkdir -p ${PROJECT_GIT}/environs/${project_env}
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/ansible
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/csshx
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/deployenv
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/nodeconf
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/pillar
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/saltconf
      mkdir -p ${PROJECT_GIT}/environs/${project_env}/statesconf
      touch ${PROJECT_GIT}/environs/${project_env}/ansible/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/csshx/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/deployenv/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/nodeconf/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/pillar/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/saltconf/readme.rst
      touch ${PROJECT_GIT}/environs/${project_env}/statesconf/readme.rst

echo "Creating file:  ${PROJECT_GIT}/environs/${project_env}/saltconf/opal_bootstrap_env"
cat > ${PROJECT_GIT}/environs/${project_env}/saltconf/opal_bootstrap_requirements <<- EOM

EOM

echo "Creating file:  ${PROJECT_GIT}/environs/${project_env}/saltconf/salt_project_env"
cat > ${PROJECT_GIT}/environs/${project_env}/saltconf/salt_project_env <<- EOM
PRJ_NAME=project_name
PRJ_ENV_NAME=${project_env}
PRJ_SALT_MASTER_NAME=salt_master_host_name
EOM
    echo
    echo
    echo "Please edit the file for correct bootstrap version: ${PROJECT_GIT}/environs/${project_env}/saltconf/opal_bootstrap_env"
    echo "Please edit the file for saltmaster information: ${PROJECT_GIT}/environs/${project_env}/saltconf/salt_project_env"
    fi
  else
    echo
    echo "Use this script from project ansible directory"
    exit 1
  fi
else
  echo "This does not look to be an git controlled repository"
  exit 1
fi
