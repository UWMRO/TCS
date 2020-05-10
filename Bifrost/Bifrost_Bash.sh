#!/bin/bash
num=`ps -ef | grep "TC_Server" | wc -l`
echo $num
if [ $num == 1 ]; then
   python ./tccv3.py
fi
