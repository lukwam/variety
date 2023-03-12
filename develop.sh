#!/usr/bin/env bash

IMAGE="variety"

docker run -it --rm \
    -e TERM="vt100" \
    -v "$(pwd)":/workspace \
    "${IMAGE}"
