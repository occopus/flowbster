#!/bin/bash

mkdir -p /var/log/flowbster

if [ ! -e /etc/flowbster-config-sys.yaml ]; then
    [ -z "$FLOWBSTER_SYS_CFG" ] && echo "Variable FLOWBSTER_SYS_CFG is not set!" && exit 1
    [ -z "$FLOWBSTER_APP_CFG" ] && echo "Variable FLOWBSTER_APP_CFG is not set!" && exit 1
    echo "$FLOWBSTER_SYS_CFG" | base64 -d > /etc/flowbster-config-sys.yaml
    echo "$FLOWBSTER_APP_CFG" | base64 -d > /etc/flowbster-config-app.yaml
fi

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

[ ! -f /.dockerenv ] && exit 0

while true; do
    sleep 60
done
