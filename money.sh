#! /bin/sh
### BEGIN INIT INFO
# Provides:          money
# Required-Start:    $network
# Required-Stop:
# Should-Start:      
# Default-Start:     S
# Default-Stop:
# Short-Description: Samantha's money web page 
# Description:       Samantha's money web page 
### END INIT INFO

. /lib/init/vars.sh
. /lib/init/mount-functions.sh
. /lib/lsb/init-functions

case "$1" in
    start)
	/home/lightning/start-money.sh &
        ;;
    restart|reload|force-reload)
        echo "Error: argument '$1' not supported" >&2
        exit 3
        ;;
    stop)
	wget -q -O /dev/null http://192.168.1.51/stop
        ;;
    *)
        echo "Usage: $0 start|stop" >&2
        exit 3
        ;;
esac

: exit 0
