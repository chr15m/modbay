#!/bin/bash

if [ -f "../../virtualenv/bin/python" ]
then
  py=../../virtualenv/bin/python
else
  py=python3
fi

./watch-spaceghost.sh > watch.log &
sgpid=$!

pd -nogui -noadc -audiobuf 150 _main.pd > pd.log 2>&1 &
pdpid=$!

$py main.py ./mods

kill $pdpid
kill $sgpid
