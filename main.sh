#!/bin/bash

py=$( `command -v ./virtualenv/bin/python` || echo "python" )

$py main.py &
guipid=$!
pd -nogui -audiobuf 50 _main.pd
kill $guipid
