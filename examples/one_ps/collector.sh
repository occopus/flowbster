#!/bin/bash
# Use > 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use > 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).

CONFFILE="/tmp/jobflow-config-sys.yaml"
LOG="jobflow-collector.log"
PIDFILE="jobflow-collector.pid"

touch $LOG

if [ -e $PIDFILE ]; then
    pid=`cat $PIDFILE`
    if [ -e /proc/$pid -a /proc/$pid/exe ]; then
        kill $pid
        sleep 1
    fi
fi

python ../../jobflow_collector.py -c $CONFFILE &
echo $! > $PIDFILE

tail -f $LOG
