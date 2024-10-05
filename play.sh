#!/usr/bin/bash

cd $(dirname "$0")
source ./venv/bin/activate

python main.py

read -sn 1 -p "Press any key to continue..."