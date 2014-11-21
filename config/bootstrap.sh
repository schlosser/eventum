#!/bin/bash


apt-get -y update

apt-get install -y  git-core
apt-get install -y  git
apt-get install -y  mongodb
apt-get install -y  python
apt-get install -y  python-dev
apt-get install -y  python-pip
apt-get install -y  python-software-properties
apt-get install -y  vim
apt-get install -y  libncurses5-dev

apt-get -y update

pip install -r /vagrant/config/requirements.txt
pip install flake8  # for local testing
gem install sass


mkdir -p /vagrant/log

# TODO: setup database and insert any data that is necessary
# service mongodb start

exit 0
