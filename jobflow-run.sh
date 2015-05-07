#!/bin/bash

mkdir -p /var/log/jobflow

if [ ! -e /var/run/jobflow-receiver.pid ]; then
    cd /home/jobflow
    python jobflow_receiver.py &
    echo $! > /var/run/jobflow-receiver.pid
else
    pid=`cat /var/run/jobflow-receiver.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find jobflow-receiver. Restarting..."
        cd /home/jobflow
        python jobflow_receiver.py &
        echo $! > /var/run/jobflow-receiver.pid
    fi
fi

if [ ! -e /var/run/jobflow-executor.pid ]; then
    cd /home/jobflow
    python jobflow_executor.py &
    echo $! > /var/run/jobflow-executor.pid
else
    pid=`cat /var/run/jobflow-executor.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find jobflow-executor. Restarting..."
        cd /home/jobflow
        python jobflow_executor.py &
        echo $! > /var/run/jobflow-executor.pid
    fi
fi

if [ ! -e /var/run/jobflow-forwarder.pid ]; then
    cd /home/jobflow
    python jobflow_forwarder.py &
    echo $! > /var/run/jobflow-forwarder.pid
else
    pid=`cat /var/run/jobflow-forwarder.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find jobflow-forwarder. Restarting..."
        cd /home/jobflow
        python jobflow_forwarder.py &
        echo $! > /var/run/jobflow-forwarder.pid
    fi
fi






