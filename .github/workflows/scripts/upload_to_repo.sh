#!/bin/bash

apt-get install -y tree > /dev/null
echo "Workdir: $(pwd)"
tree ./artifact