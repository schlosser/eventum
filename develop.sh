#! /bin/bash
mongod &
virtualenv --no-site-packages .
pip install -r requirements.txt
bin() { source $1/activate; }
