#!/bin/bash


apt-get -y update

apt-get install -y \
    git-core \
    git \
    mongodb \
    python \
    python-pip \
    python-dev \
    python-software-properties \
    vim     # debugging

apt-get update
pip install -r /vagrant/config/requirements.txt
pip install flake8  # for local testing
gem install sass


# TODO: setup database and insert any data that is necessary
service mongod start

exit 0
