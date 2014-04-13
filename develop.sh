#! /bin/bash
virtualenv --no-site-packages .
pip install -r requirements.txt
mongod &
source bin/activate
