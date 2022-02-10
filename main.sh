#!/bin/bash

py=$( `command -v ./virtualenv/bin/python` || echo "python" )

pd -nogui -audiobuf 50 _main.pd &
pdpid=$!
$py main.py
kill $pdpid
