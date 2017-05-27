#!/bin/bash
num=`ps -ef | grep "test" | wc -l`
echo $num
if [ $num == 1 ]; then
   python /home/mro/TCC/tccv3.py
fi
