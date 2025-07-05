#!/bin/bash
scriptdir=/home/pi/RetroPie-Setup
source "$scriptdir/scriptmodules/system.sh"
source "$scriptdir/scriptmodules/helpers.sh"
source "$scriptdir/scriptmodules/inifuncs.sh"
#source "$scriptdir/scriptmodules/packages.sh"
joy2keyStart kcub1 kcuf1 kcuu1 kcud1 0x20 0x0a 0x58 0x59
echo "Running $1";
cd /home/pi/modbay
./main.sh > /home/pi/modbay_run.log 2>&1
joy2keyStop
echo "Boot script exit"
sleep 10
