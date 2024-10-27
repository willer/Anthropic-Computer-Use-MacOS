#!/bin/bash

moresecure=true

if [ "$moresecure" = true ]; then
    echo "Using separate network"
    docker run \
        -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
        -v /Users/swiller/.anthropic:/home/computeruse/.anthropic \
        -p 5900:5900 \
        -p 8501:8501 \
        -p 6080:6080 \
        -p 8080:8080 \
        -e WIDTH=1600 \
        -e HEIGHT=1080 \
        -it ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
else
    echo "Using host ports"
    docker run \
        -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
        -v /Users/swiller/.anthropic:/home/computeruse/.anthropic \
        --network host \
        -e WIDTH=1600 \
        -e HEIGHT=1080 \
        -it ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
fi
