#! /bin/bash
virtualenv --no-site-packages .
source bin/activate
pip install -r requirements.txt
mongod &
