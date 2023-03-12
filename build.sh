#!/usr/bin/env bash

IMAGE="variety"

# docker build -t "${IMAGE}" .
pack build "${IMAGE}" --builder gcr.io/buildpacks/builder
