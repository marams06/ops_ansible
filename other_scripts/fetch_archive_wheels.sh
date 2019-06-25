#!/usr/bin/env bash

#####################################################
##
## This utility is used to download the wheels and cache it locally
## It is used by ansible to bootstrap python environment.
## Ashish R Vidyarthi
#####################################################


cur_dir=`pwd`
SCRIPT_PATH=$(cd $(dirname "$0") && pwd -P)
SCRIPT_FILE=$(basename $0)
OPS_ANSIBLE_PATH=$(dirname "$SCRIPT_PATH")
EXT_GIT_PATH=$(dirname "$OPS_ANSIBLE_PATH")
SALT_PROJECT_GIT_PATH=$(dirname "$EXT_GIT_PATH")
TIMESTAMP=`date +"%Y-%m-%d %H:%M:%S"`

export SALT_PROJECT_GIT_PATH=${SALT_PROJECT_GIT_PATH}
mkdir -p $SALT_PROJECT_GIT_PATH/wheelarchive/wheels

if [ $# -lt 1 ]
then
  echo "Provide wheels linux platform option: oel6|oel7"
  exit 1
fi

linux_platform=$1

# Check if wheels are already archived or not
if [ ! -f $SALT_PROJECT_GIT_PATH/wheelarchive/wheelarchive.tar.gz ]; then

	for package in `cat ${SCRIPT_PATH}/${linux_platform}_packages.txt`
	do
		if [ ! -f $SALT_PROJECT_GIT_PATH/wheelarchive/wheels/$package ]; then
			echo "$package needs to be downloaded"
			builtin cd $SALT_PROJECT_GIT_PATH/wheelarchive/wheels
			curl -s -H "X-JFrog-Art-Api:$ARTIFACTORY_READER_API" -O https://artifacts.apple.com/aml-infraeng-release-local/com/apple/athena/packages/wheel/$linux_platform/$package
			builtin cd $cur_dir
		else
			echo "Skip downloading $package"
		fi
	done
	builtin cd $SALT_PROJECT_GIT_PATH/wheelarchive
	tar czf wheelarchive.tar.gz wheels
	builtin cd $cur_dir
fi
