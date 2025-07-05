#!/bin/bash

# Get the directory where the script is located
APP_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

scriptdir=/home/pi/RetroPie-Setup
source "$scriptdir/scriptmodules/system.sh"
source "$scriptdir/scriptmodules/helpers.sh"
source "$scriptdir/scriptmodules/inifuncs.sh"
#source "$scriptdir/scriptmodules/packages.sh"
joy2keyStart kcub1 kcuf1 kcuu1 kcud1 0x20 0x0a 0x58 0x59
cd "${APP_DIR}"
date > modbay_run.log
echo "Running modbay from ${APP_DIR}" >> modbay_run.log
./main.sh >> modbay_run.log 2>&1
joy2keyStop
echo "Boot script exit"
sleep 10
