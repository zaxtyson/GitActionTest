#!/bin/bash

function install_dependencies() {
    echo "Installing dependencies..."
    # we are running in action runner, so we should use `sudo`
    sudo apt-get update
    sudo apt-get install -y curl >/dev/null
}

function upload_to_repo() {
    repo_api="https://repo.zaxtyson.workers.dev/v1/upload"

    # compress the deb packages
    echo "Compressing deb packages..."
    cd artifact/artifact # ${workdir}/artifact/artifact/{debian,ubuntu}/...
    tar -zcvf artifact.tar.gz *
    echo ""

    # Upload to repo server
    cnt=1
    max_retry=3
    while true; do
        echo "[$cnt] Uploading to $repo_api ..."
        resp=$(curl -s -X PUT --data-binary @artifact.tar.gz -H "Authorization: token $UPLOAD_TOKEN" $repo_api)
        cnt=$((cnt + 1))

        if [ "$resp"x == "ok"x ]; then
            echo "Upload success!"
            exit 0
        fi

        echo "Server response: $resp"
        if [ $cnt -le $max_retry ]; then
            echo "Upload failed, retry in 10 seconds..."
            echo ""
            sleep 10
        else
            echo "Upload failed!"
            exit 1
        fi
    done
}

function main() {
    install_dependencies
    upload_to_repo
}

main
