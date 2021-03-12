#!/bin/bash

# Script gathers system information about main storage devices,
# forms JSON file and posts it to SDT API

# DEPENDENCIES
# jq - Command-line JSON processor

# Main variables
# Server IP or resolvable fqdn
SERVER="192.168.0.2"
# List of mounted storage devices to be monitored. Add -x options for file system types you want to exclude
DEVICE_LIST=$(df -x squashfs -x tmpfs -x devtmpfs -x overlay --output=target | tail -n +2)
# Threshold values of used space in percentage to determine device state
ALERT=90 # If device usage in percents is greater than this value, device will be assigned alert state
WARNING=80 # If device usage in percents is greater than this value, device will be assigned warning state
# Temporary request file location
REQUEST="/tmp/request"
# Flag for QUIET mode
QUIET=false
# Server timeout in seconds
TIMEOUT=5
# API url
URI="http://$SERVER:5000/api/v1/devices"
# Regular expression for matching integers
INTEGERS_RE='^[0-9]+$'
# Help message
HELP="
    Usage: $(basename "${BASH_SOURCE[0]}") [-h] [-q] [options] [args]\n
    This is linux agent for storage device monitoring application. For more information check https://github.com/f5AFfMhv\n
    Available options:\n
        \t -h   \tPrint this help and exit\n
        \t -q   \tQuiet stdout\n
        \t -s   \tServer IP/FQDN\n
        \t -a   \tThreshold device usage in percents for device status ALERT\n
        \t -w   \tThreshold device usage in percents for device status WARNING\n
    Example:\n
        \t ./$(basename "${BASH_SOURCE[0]}") -q -s 192.168.100.100 -a 90 -w 80
"

# Parse input arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -q) QUIET=true ;;
        -s) SERVER=$2
        shift ;;
        -a) ALERT=$2
        shift ;;
        -w) WARNING=$2
        shift ;;
    *) echo -e $HELP
      exit 0 ;;
esac
shift
done

# Check if jq installed
if ! command -v jq &> /dev/null; then
    echo "Please install jq - command-line JSON processor."
    exit 1
fi
# Check if server is available
if [[ -z $(curl --connect-timeout $TIMEOUT -Is http://$SERVER:5000) ]]; then
    echo "Server $SERVER unavailable"
    exit 1
fi
# Check if alert threshold is a number
if ! [[ $ALERT =~ $INTEGERS_RE ]] ; then
    echo "Alert threshold is not a valid number"
    exit 1
fi
# Check if warning threshold is a number
if ! [[ $WARNING =~ $INTEGERS_RE ]] ; then
    echo "Warning threshold is not a valid number"
    exit 1
fi

# For every storage device in list, get information about its size, free space and usage in percentage.
for DEVICE in $DEVICE_LIST; do
    if [[ $DEVICE != /boot* ]]; then
        SIZE=$(df -BM $DEVICE | tail -n +2 | awk '{print $2}')
        FREE=$(df -BM $DEVICE | tail -n +2 | awk '{print $4}')
        USE=$(df -h $DEVICE | tail -n +2 | awk '{print $5}')
        # From gathered information determine storage device state (alert, warning, normal)
        if (( ${USE%?} > $ALERT )); then
            STATE=alert
        elif (( ${USE%?} > $WARNING )); then
            STATE=warning
        else
            STATE=normal
        fi
        # Make API request for hostname and device. If device ID not found - create record, else - update values
        echo "$URI?host=$HOSTNAME&device=$DEVICE" > $REQUEST
        # Try to get device ID from request
        ID=$(curl -s $(cat $REQUEST) | jq '.[].id' 2>/dev/null)
        if [[ -z $ID ]]; then
            if [[ $QUIET != true ]]; then
                echo "Device $DEVICE doesnt exist. Creating..."
            fi
            # Form API request in JSON format (\" preserves " character in JSON request)
            # ${var%?} - removes last symbol from variable
            echo {\"host\":\"$HOSTNAME\", \
                \"device\":\"$DEVICE\", \
                \"state\":\"$STATE\", \
                \"size_mb\":\"${SIZE%?}\", \
                \"free_mb\":\"${FREE%?}\", \
                \"used_perc\":\"${USE%?}\"} > $REQUEST

            # Make API POST call
            if [[ $QUIET == true ]]; then
                curl -s \
                    --header "Content-type: application/json" \
                    --request POST \
                    --data @$REQUEST \
                    $URI \
                    > /dev/null
            else
                curl -s \
                    --header "Content-type: application/json" \
                    --request POST \
                    --data @$REQUEST \
                    $URI \
                    | jq
            fi
        else
            if [[ $QUIET != true ]]; then
                echo "Device $DEVICE exists with id: $ID. Updating..."
            fi
            # Form API request in JSON format (\" preserves " character in JSON request)
            # ${var%} - removes last symbol from variable
            echo {\"id\":\"$ID\", \
                \"state\":\"$STATE\", \
                \"size_mb\":\"${SIZE%?}\", \
                \"free_mb\":\"${FREE%?}\", \
                \"used_perc\":\"${USE%?}\"} > $REQUEST

            # Make API PUT call
            if [[ $QUIET == true ]]; then
                curl -s \
                    --header "Content-type: application/json" \
                    --request PUT \
                    --data @$REQUEST \
                    $URI \
                    > /dev/null
            else
                curl -s \
                    --header "Content-type: application/json" \
                    --request PUT \
                    --data @$REQUEST \
                    $URI \
                    | jq
            fi
        fi

        # Remove temporary file
        rm -f $REQUEST 
    fi
done


