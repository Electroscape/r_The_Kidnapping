#!/bin/bash

sudo apt update -y

# shellcheck disable=SC2164
python3 -m venv venv
source venv/bin/activate

pip3 install -r requirements.txt