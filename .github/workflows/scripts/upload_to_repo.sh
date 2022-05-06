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
    update_file="update.tar.gz"
    echo "Compressing deb packages..."
    tar -zcvf $update_file artifact
    echo ""
    ls -hal $update_file
    echo ""

    # Upload to repo server
    cnt=1
    max_retry=3
    while true; do
        echo "[$cnt] Uploading $update_file to $repo_api ..."
        resp=$(curl -s -X PUT -F "update=@$update_file" -H "Authorization: token $UPLOAD_TOKEN" $repo_api)
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
