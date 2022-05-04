#!/bin/bash

function install_dependencies() {
    echo "Installing dependencies..."
    apt-get update
    apt-get install -y curl >/dev/null
}

function upload_to_repo() {
    repo_api="http://repo.zaxtyson.cn:8086/v1/upload"

    # compress the deb packages
    echo "Compressing deb packages..."
    tar -zcvf artifact.tar.gz artifact
    echo ""

    # Upload to repo server
    cnt=1
    max_retry=3
    while true; do
        echo "[$cnt] Uploading to $repo_api ..."
        resp=$(curl -s -X PUT -d @artifact.tar.gz -H "Authorization: token $UPLOAD_TOKEN" $repo_api)
        cnt=$((cnt + 1))

        if [ "$resp"x == "ok"x ]; then
            echo "Upload success!"
            exit 0
        fi

        echo "Server response: $resp"
        if [ $cnt -le $max_retry ]; then
            echo "Upload failed, retry in 5 seconds..."
            echo ""
            sleep 1
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
