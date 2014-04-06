#! /bin/bash
virtualenv --no-site-packages .
source bin/activate
mongod &
