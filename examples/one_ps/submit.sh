#!/bin/bash
# Use > 1 to consume two arguments per pass in the loop (e.g. each
# argument has a corresponding value to go with it).
# Use > 0 to consume one or more arguments per pass in the loop (e.g.
# some arguments don't have a corresponding value to go with it such
# as in the --default example).

JOBFILE="jobflow-job-with-content.yaml"
HOSTIP="192.168.153.153"
NUM=1

if [[ $# < 2 ]]; then
        echo "Usage: $0 -h [hostip] -j [jobfile] default: \"-h $HOSTIP -j $JOBFILE -n $NUM\""
fi

while [[ $# > 0 ]]
do
key="$1"

case $key in
    -n|--number)
    NUM="$2"
    shift # past argument
    ;;
    -h|--hostip)
    HOSTIP="$2"
    shift # past argument
    ;;
    -j|--jobfile)
    JOBFILE="$2"
    shift # past argument
    ;;
    *)
    ;;
esac
shift # past argument or value
done
echo HOSTIP : "$HOSTIP"
echo JOBFILE: "$JOBFILE" 
if [ "$HOSTIP" == "" ]; then
    echo "ERROR: no hostip defined! Use -h 1.2.3.4 "
else
    for a in `seq $NUM`; do
        echo "Instance $a :"
        python ../../jobflow_submit.py $JOBFILE http://$HOSTIP:5000/jobflow ;
    done
fi

