#!/bin/bash
PYTHON=/usr/local/bin/python3
ENCODING=zh_CN.UTF-8

# get the running script file full path
get_script_dir() {
    oldwd=`pwd`
    rw=`dirname $0`
    cd $rw
    sw=`pwd`
    cd $oldwd
    echo $sw
}

RUN_PATH=`get_script_dir`
APP_PATH=`dirname $RUN_PATH`
MAIN_APP=$APP_PATH/ia_icbc_server.py

app_pid=0
check_pid() {
    UNIX_PS=`ps -ef | grep $MAIN_APP | grep -v 'grep'`
    if [ -n "$UNIX_PS" ]; then
        app_pid=`echo $UNIX_PS | awk '{print $2}'`
    else
        app_pid=0
    fi
}

check_pid

if [ $app_pid -ne 0 ]; then
      echo "================================"
      echo "warn: $MAIN_APP already started! (pid=$app_pid)"
      echo "================================"
      exit 0
fi

echo -n "Starting $MAIN_APP ..."

export LC_ALL=$ENCODING
$PYTHON $MAIN_APP >/dev/null 2>&1 &

sleep 0.5

check_pid

if [ $app_pid -ne 0 ]; then
    echo "(pid=$app_pid) [OK]"
else
    echo "[Failed]"
    exit 1
fi

exit 0
