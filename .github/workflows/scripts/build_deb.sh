#!/bin/bash

function install_dependencies() {
    echo "Installing dependencies..."
    apt-get update
    apt-get install -y build-essential libssl-dev python3-pip git lsb-release >/dev/null
    pip3 install --upgrade cmake
}

function build_workflow() {
    echo "Building workflow..."
    git clone https://github.com/sogou/workflow
    cd workflow
    mkdir build
    cd build
    cmake ..
    make -j8
    cd ..
}

function export_env() {
    export VERSION="0.10.1"
    export ARCH="amd64"
    export DIST_CODE=$(lsb_release -cs)
}

function build_libworkflow1() {
    mkdir -p libworkflow1/usr/lib
    mkdir -p libworkflow1/DEBIAN
    cp -r ./_lib/libworkflow.* libworkflow-dev/usr/lib/
    echo "Package: libworkflow1
Source: workflow
Version: ${VERSION}
Priority: optional
Architecture: ${ARCH}
Section: universe/libdevel
Depends: libssl-dev
Maintainer: zaxtyson <zaxtyson@foxmail.com>
Homepage: https://github.com/sogou/workflow
Bugs: https://github.com/sogou/workflow/issues
Description: Parallel computing and asynchronous web server engine" >libworkflow1/DEBIAN/control
    dpkg -b libworkflow1/ libworkflow1_${VERSION}-1~${DIST_CODE}_${ARCH}.deb
}

function build_libworkflow_dev() {
    mkdir -p libworkflow-dev/usr/include
    mkdir -p libworkflow-dev/DEBIAN
    cp -r ./_include/workflow libworkflow-dev/usr/include/
    echo "Package: libworkflow-dev
Source: workflow
Version: ${VERSION}
Priority: optional
Architecture: ${ARCH}
Section: universe/libdevel
Depends: libworkflow1
Maintainer: zaxtyson <zaxtyson@foxmail.com>
Homepage: https://github.com/sogou/workflow
Bugs: https://github.com/sogou/workflow/issues
Description: Parallel computing and asynchronous web server engine" >libworkflow-dev/DEBIAN/control
    dpkg -b libworkflow-dev/ libworkflow-dev_${VERSION}-1~${DIST_CODE}_${ARCH}.deb
}

function move_artifact_path() {
    if [ ! -d /output ]; then
        mkdir -p /output/deb
    fi
    mv *.deb /output/deb/
}

function main() {
    install_dependencies
    export_env
    build_workflow
    build_libworkflow1
    build_libworkflow_dev
    move_artifact_path
}

main
