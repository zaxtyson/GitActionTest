#!/bin/bash

# install tools
apt-get update
apt-get install -y build-essential libssl-dev python3-pip git lsb-release > /dev/null
pip3 install --upgrade cmake

# build library
git clone https://github.com/sogou/workflow 
cd workflow
mkdir build
cd build
cmake ..
make -j8

# build deb
VERSION=$1
ARCH="amd64"
DIST_CODE=$(lsb_release -cs)

mkdir -p libworkflow-dev/usr/{include,lib}
mkdir -p libworkflow-dev/DEBIAN
cp -r ../_include/workflow libworkflow-dev/usr/include/
cp -r ../_lib/libworkflow.* libworkflow-dev/usr/lib/

echo "Package: libworkflow-dev
Source: workflow
Version: $VERSION
Priority: optional
Architecture: $ARCH
Section: universe/libdevel
Depends: libssl-dev
Maintainer: zaxtyson <zaxtyson@foxmail.com>
Homepage: https://github.com/sogou/workflow
Bugs: https://github.com/sogou/workflow/issues
Description: Parallel computing and asynchronous web server engine
 Workflow can be used as a scalable web server to handle a variety
 of server workflows. It can be used to orchestrate complex
 relationships between computing and networking. Workflow currently
 supports protocols for HTTP, Redis, MySQL and Kafka." > libworkflow-dev/DEBIAN/control

 dpkg -b libworkflow-dev/ libworkflow-dev_$VERSION-1~$DIST_CODE_$ARCH.deb