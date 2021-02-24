
# Script gathers system information about main storage devices,
# forms JSON file and posts it to "Server Disk Space" API

# DEPENDENCIES
# 

# Main variables
# "Server Disk Space" server IP or resolvable fqdn
$SERVER="192.168.0.2"
# Threshold values of free space in GB to determine device state
$ALERT=10 # If device has less free space in GB than this value, device will be assignet alert state
$WARNING=25 # If device has less free space in GB than this value, device will be assignet warning state
# Flag for QUIET mode
$QUIET=0
# Value for disk size conversion to GB
$GB=1073741824
# Help message
$HELP="
    Usage: SDT-windows-agent.ps1 [-h] [-q] [options] [args]\n
    This is linux agent for storage device monitoring application. For more information check https://github.com/f5AFfMhv\n
    Available options:\n
        \t -h   \tPrint this help and exit\n
        \t -q   \tDon't output anything\n
        \t -s   \tServer IP/FQDN\n
        \t -a   \tThreshold value in GB for device status ALERT\n
        \t -w   \tThreshold value in GB for device status WARNING\n
    Example:\n
        \t ./disk_space.sh -s 192.168.100.100 -a 10 -w 20
"
Set-ExecutionPolicy Unrestricted -Force
# Determine server name
$name = (Get-CimInstance -ClassName Win32_ComputerSystem).name

# Get information on system logical volumes which are not CD-ROM, without drive letter or with size attribute equal to 0
$volumes = (Get-Volume |
    Where-Object {$_.DriveLetter -ne $Null} | 
    Where-Object {$_.DriveType -ne "CD-ROM"} |
    Where-Object {$_.Size -ne 0})


foreach ($volume in $volumes){
    $device = $Volume.DriveLetter + ": " + $Volume.FileSystemLabel
    $size = [math]::floor($Volume.Size/$GB)
    $free = [math]::floor($Volume.SizeRemaining/$GB)
    if ($free -le $ALERT) 
        {$state="alert"} 
    elseif ($free -le $WARNING) 
        {$state="warning"}
    else 
        {$state="normal"}
    $used_perc = [math]::floor(($size-$free)*100/$size)

    Write-Host $name
    Write-Host $device
    Write-Host $state
    Write-Host $size
    Write-Host $free
    Write-Host $used_perc
    Write-Host "------------------------------"

    # $URI = "http://" + $SERVER + ":5000/api/v1/resources/servers?name=" + $name + "&device=" + $device
    # $exists = (Invoke-RestMethod -Uri $URI).status

    $URI = "http://" + $SERVER + ":5000/api/v1/resources/servers"
    $Body = @{
        name = $name
        device = $device
        state = $state
        size_gb = $size
        free_gb = $free
        used_perc = $used_perc}

    Invoke-RestMethod -Method 'Post' -Uri $URI -Body $Body
    }
#Invoke-WebRequest -Uri "http://192.168.0.2:5000/api/v1/resources/servers/all"
