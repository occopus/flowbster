#!/bin/bash
# Use > 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use > 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).

COLLECTOR_BIN="`dirname $0`/flowbster_collector.py"
PIDFILE="flowbster-collector.pid"
LOGFILE="flowbster-collector.log"

if [[ $# < 1 ]]; then
		echo "Usage: $0 [-s|--start] [-d|--destroy]"
        exit 1
fi

while [[ $# > 0 ]]
do 
key="$1"

case $key in
    -d|--destroy)
    shift
    if [ -e $PIDFILE ]; then
        pid=`cat $PIDFILE`
        if [ -e /proc/$pid -a /proc/$pid/exe ]; then
            kill $pid
            sleep 1
            rm -f $PIDFILE
        fi
    fi
    ;;
    -s|--start)
    shift
    if [ -e $PIDFILE ]; then
        pid=`cat $PIDFILE`
        if [ -e /proc/$pid -a /proc/$pid/exe ]; then
            kill $pid
            sleep 1
            rm -f $PIDFILE
        fi
    fi
    python $COLLECTOR_BIN -c $CONFFILE &
    echo $! > $PIDFILE
    touch $LOGFILE
    tail -f $LOGFILE
    ;;
    *)
    echo "WARNING: unknown argument: $key"
    shift
    ;;
esac
done

exit 0
 
