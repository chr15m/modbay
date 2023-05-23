#!/bin/sh

tail -f log &
xterm -fa "Courier Prime" -fs 14 -geometry 53x20 -e 'eval "$(direnv export bash)"; ./main.sh --gui; read done'
pkill -P $$
