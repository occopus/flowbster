#!/bin/sh

JFDIR="../.."
JOBFILE="jobflow-config-job-with-content.yaml"
TARGETIP="192.168.152.242"
echo "Jobfile  : $JOBFILE"
echo "Target ip: $TARGETIP"
python $JFDIR/jobflow_submit.py $JOBFILE http://$TARGETIP:5000/jobflow
