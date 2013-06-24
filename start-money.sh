#!/bin/sh
while [ "x`ping -c 1 192.168.1.1 | grep Unreachable`" != "x" ]; do
	sleep 5
done

cd /home/lightning
sleep 10
python /home/lightning/money.py > /dev/null 2>&1 &
sleep 5
wget -q -O /dev/null http://127.0.0.1/

