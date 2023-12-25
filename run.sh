#!/bin/sh

PROXY_CMD="python ./proxy"
SCRAP_CMD=./app/build/app

(trap 'kill 0' SIGINT; ${PROXY_CMD} 4 & ${SCRAP_CMD} & wait)