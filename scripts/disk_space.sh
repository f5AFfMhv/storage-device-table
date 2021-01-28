#!/bin/bash

# Script gathers system information about main storage devices,
# forms JSON file and posts it to "Server Disk Space" API

# Main variables
# "Server Disk Space" server IP or resolvable fqdn
SERVER="192.168.0.2"
# List of mounted storage devices to be monitored
MOUNT_LIST=("/mint--vg-root" "/mnt/DATA")
# Treshold values of free space in GB to determine device state
ALERT=80 # If device has less free space in GB than this value, device will be assignet alert state
WARNING=150 # If device has less free space in GB than this value, device will be assignet warning state
# Temporary request file location
REQUEST="/tmp/request"

# For every storage device in list, get information about its size, free space and usage in percentage.
for MOUNT in ${MOUNT_LIST[@]}; do
    SIZE=$(df -BGB | grep $MOUNT | awk '{print $2}')
    FREE=$(df -BGB | grep $MOUNT | awk '{print $4}')
    USE=$(df -h | grep $MOUNT | awk '{print $5}')
    # From gathered information determine storage device state (alert, warning, normal)
    if (( ${FREE%??} < $ALERT )); then
        STATE=alert
    elif (( ${FREE%??} < $WARNING )); then
        STATE=warning
    else
        STATE=normal
    fi
    echo "$MOUNT size: $SIZE, free: $FREE, usage: $USE, state: $STATE"
    # From API request device from hostname and mount point. If device ID not found - create record, else - update values
    echo "http://$SERVER:5000/api/v1/resources/servers?name=$HOSTNAME&mount=$MOUNT" > $REQUEST
    # Try to get device ID from request
    ID=$(curl -s $(cat $REQUEST) | grep '"id"' | awk '{print $2}' | sed 's/,//')
    if [[ -z $ID ]]; then
        echo "Device $MOUNT doesnt exist. Creating..."
        # Form API request in JSON format (\" preserves " character in JSON request)
        # ${var%??} - removes last 2 symbols from variable
        echo {\"name\":\"$HOSTNAME\", \
            \"mount\":\"$MOUNT\", \
            \"state\":\"$STATE\", \
            \"size_gb\":${SIZE%??}, \
            \"free_gb\":${FREE%??}, \
            \"used_perc\":${USE%?}} > $REQUEST

        # Make API POST call
        curl \
            --header "Content-type: application/json" \
            --request POST \
            --data @$REQUEST \
            http://$SERVER:5000/api/v1/resources/servers
    else
        echo "Device $MOUNT exists with id: $ID. Updating..."
        # Form API request in JSON format (\" preserves " character in JSON request)
        # ${var%??} - removes last 2 symbols from variable
        echo {\"id\":\"$ID\", \
            \"state\":\"$STATE\", \
            \"size_gb\":${SIZE%??}, \
            \"free_gb\":${FREE%??}, \
            \"used_perc\":${USE%?}} > $REQUEST

        # Make API PUT call
        curl \
            --header "Content-type: application/json" \
            --request PUT \
            --data @$REQUEST \
            http://$SERVER:5000/api/v1/resources/servers
    fi

    # Remove temporary file
    rm -f $REQUEST 
done


