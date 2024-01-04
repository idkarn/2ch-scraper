#!/bin/sh

PROXY_CMD="python ./proxy/main.py"
SCRAP_CMD=./app/build/app

(trap 'kill -INT 0' SIGINT; ${PROXY_CMD} & ${SCRAP_CMD} & wait)