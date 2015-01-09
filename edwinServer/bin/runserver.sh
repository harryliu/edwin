#!/bin/bash

#set python executable 
export PYTHON_BIN=/home/user1/pythonenv/python27/scripts/python

# base path, it is the parent of root package path  
export BASE_PATH=/home/user1/trunk/workspace/Edwin

# set your python script file. Please be noticed to trim the tailed space of file name 
export MY_PY_SCRIPT=runserver.py


#=================================
# do not change the following code
#=================================
export PYTHONPATH=$BASE_PATH

export SCRIPT_PATH=$BASE_PATH/edwinServer/web
export BIN_PATH=$BASE_PATH/edwinServer/bin
export LOCK_FILE=$BIN_PATH/locks/$MY_PY_SCRIPT.lock
export MY_PY_FILE=$SCRIPT_PATH/$MY_PY_SCRIPT

cnt=`ls $LOCK_FILE|wc -l`
if [ ${cnt} -lt 1 ]
then
    touch $LOCK_FILE
    $PYTHON_BIN $MY_PY_FILE
    rm $LOCK_FILE
fi

