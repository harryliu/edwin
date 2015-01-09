#!/bin/bash

#load profile
source ~/.bash_profile

# set jython executable 
JYTHON_BIN=/home/user1/pythonenv/jython271/jython.sh

# base path, it is the parent of root package path 
BASE_PATH=/home/user1/trunk/workspace/Edwin

# set your python script file. Please be noticed to trim the tailed space of file name 
MY_PY_SCRIPT=detect_threadstuck_in_log_file.py


#=================================
# do not change the following code
#=================================
JYTHONPATH=$BASE_PATH

SCRIPT_PATH=$BASE_PATH/edwinAgent/agents
BIN_PATH=$BASE_PATH/edwinAgent/bin
LOCK_FILE=$BIN_PATH/locks/$MY_PY_SCRIPT.lock
MY_PY_FILE=$SCRIPT_PATH/$MY_PY_SCRIPT

cnt=`ls $LOCK_FILE|wc -l`
if [ ${cnt} -lt 1 ]
then
    touch $LOCK_FILE
    $JYTHON_BIN $MY_PY_FILE
    rm $LOCK_FILE
fi

