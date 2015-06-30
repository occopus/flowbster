#!/bin/bash
# Use > 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use > 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).

for pid in `ls *.pid`;
do
    echo "pidfile: $pid"
    kill `cat $pid`
    rm $pid
done
ps aux | grep jobflow

