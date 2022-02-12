#!/bin/bash

if [ -f "../../virtualenv/bin/python" ]
then
  py=../../virtualenv/bin/python
else
  py=python3
fi

pd -nogui -audiobuf 50 _main.pd &
pdpid=$!
$py main.py
kill $pdpid
