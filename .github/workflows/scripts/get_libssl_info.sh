#!/bin/bash

apt-get install lsb-release libssl-dev -y >/dev/null
mkdir /output
release_file="$(lsb_release -is)_$(lsb_release -rs)_$(lsb_release -cs).txt"
lsb_release -a > /output/${release_file}
echo "================" >> /output/${release_file}
apt show libssl-dev -a >> /output/${release_file}