#!/usr/bin/env bash

crontab /root/crontab
echo "Running CRON server"
exec cron -f
