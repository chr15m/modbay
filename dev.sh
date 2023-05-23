#!/bin/sh

tail -f log &
( for i in `seq 5`; do wmctrl -x -a xterm.Xterm; sleep 1; done ) &
xterm -fa "Courier Prime" -fs 14 -geometry 53x20+550+50 -e 'eval "$(direnv export bash)"; ./main.sh --gui; read done'
pkill -P $$
