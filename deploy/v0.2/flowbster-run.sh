#!/bin/bash

mkdir -p /var/log/flowbster

if [ ! -e /var/run/flowbster-receiver.pid ]; then
    cd /usr/bin
    python flowbster_receiver.py &
    echo $! > /var/run/flowbster-receiver.pid
else
    pid=`cat /var/run/flowbster-receiver.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find flowbster-receiver. Restarting..."
        cd /usr/bin
        python flowbster_receiver.py &
        echo $! > /var/run/flowbster-receiver.pid
    fi
fi

if [ ! -e /var/run/flowbster-executor.pid ]; then
    cd /usr/bin
    python flowbster_executor.py &
    echo $! > /var/run/flowbster-executor.pid
else
    pid=`cat /var/run/flowbster-executor.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find flowbster-executor. Restarting..."
        cd /usr/bin
        python flowbster_executor.py &
        echo $! > /var/run/flowbster-executor.pid
    fi
fi

if [ ! -e /var/run/flowbster-forwarder.pid ]; then
    cd /usr/bin
    python flowbster_forwarder.py &
    echo $! > /var/run/flowbster-forwarder.pid
else
    pid=`cat /var/run/flowbster-forwarder.pid`
    if [ ! -e /proc/$pid -a /proc/$pid/exe ]; then
        echo "Cannot find flowbster-forwarder. Restarting..."
        cd /usr/bin
        python flowbster_forwarder.py &
        echo $! > /var/run/flowbster-forwarder.pid
    fi
fi






