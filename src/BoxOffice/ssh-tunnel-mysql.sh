#!/bin/bash
#
# Script: ssh-tunnel-mysql.sh
# Purpose: open and keep alive the tunneling and mysql port forwarding
# Author: beppe miletto
# Version: $Id: Proto.sh,v 0.1 2017/10/25 nichols Exp $
#

echo "opening the port 3306 on ssh connection"

ssh -n -N -f -L 3306:127.0.0.1:3306 ltc@teatrocambiano.sytes.net

python3 testThreads.py

