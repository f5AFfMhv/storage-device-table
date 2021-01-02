#!/bin/bash

SERVER="localhost"
MOUNT_LIST=("/mint--vg-root" "/mnt/backup" "/mnt/DATA")

for MOUNT in ${MOUNT_LIST[@]}; do
    SIZE=$(df -h | grep $MOUNT | awk '{print $2}')
    SZ=${SIZE%?}
    FREE=$(df -h | grep $MOUNT | awk '{print $4}')
    FR=${FREE%?}
    USE=$(df -h | grep $MOUNT | awk '{print $5}')
    US=${USE%?}
    STATE="normal"
    curl -i -H "Content-Type: application/json" -X POST -d '{"name":$HOSTNAME, "mount":$MOUNT, "state":$STATE, "size_gb":$((SZ)), "free_gb":$((FR)), "used_perc":$((US))}' http://$SERVER:5000/api/v1/resources/servers
done

echo "'{"name":$HOSTNAME, "mount":$MOUNT, "state":$STATE, "size_gb":$SZ, "free_gb":$FR, "used_perc":$US}' http://$SERVER:5000/api/v1/resources/servers"
#curl -i -H "Content-Type: application/json" -X POST -d '{"name":$HOSTNAME, "mount":$mount, "state":$state, "size_gb":$size, "free_gb":$free, "used_perc":$used}' http://$SERVER:5000/api/v1/resources/servers