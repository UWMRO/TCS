#!/bin/bash
num=`ps -ef | grep "TCC" | wc -l`
echo $num
sleep 5
if [ $num == 1 ]; then
   python /home/mro/TCC/tccv3.py
fi
