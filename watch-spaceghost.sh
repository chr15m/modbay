#!/bin/bash

sendit () {
  echo "Sending $1 for Spaceghost presence."
  echo "$1 ;" > /dev/udp/localhost/33333
  echo "Done."
}

while [ 1 ]
do
  ping -w 1 -c 1 spaceghost.local >/dev/null 2>/dev/null && sendit "1" || sendit "0"
  sleep 1
done
