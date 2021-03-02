
# Script gathers system information about main storage devices,
# forms JSON request and posts it to SDT API

# Main variables
# param (
#     # Flag for QUIET mode
#     [bool]$QUIET=$false,
#     # Server IP or resolvable fqdn
#     [string]$SERVER="192.168.0.2",
#     # Threshold values of free space in GB to determine device state
#     [int]$ALERT=5, # If device has less free space in GB than this value, device will be assignet alert state
#     [int]$WARNING=25 # If device has less free space in GB than this value, device will be assignet warning state
# )
$QUIET=$false
# Server IP or resolvable fqdn
$SERVER="192.168.0.2"
# Threshold values of free space in GB to determine device state
$ALERT=5 # If device has less free space in GB than this value, device will be assignet alert state
$WARNING=50 # If device has less free space in GB than this value, device will be assignet warning state
# API url
$URI = "http://" + $SERVER + ":5000/api/v1/devices"
# Byte value for disk size conversion to MB
$MB=1048576 # 1 MB = 1048576 B
# Help message
$HELP="
    Usage: SDT-windows-agent.ps1 [-h] [-q] [options] [args]\n
    This is linux agent for storage device monitoring application. For more information check https://github.com/f5AFfMhv\n
    Available options:\n
        \t -h   \tPrint this help and exit\n
        \t -q   \tQuiet stdout\n
        \t -s   \tServer IP/FQDN\n
        \t -a   \tThreshold free space in GB for device status ALERT\n
        \t -w   \tThreshold free space in GB for device status WARNING\n
    Example:\n
        \t ./SDT-windows-agent.ps1 -s 192.168.100.100 -a 10 -w 20
"

# Determine server name
$hostname = (Get-CimInstance -ClassName Win32_ComputerSystem).name

# Convert threshold values from GB to MB
$ALERT=$ALERT * 1024
$WARNING=$WARNING * 1024

# Get information on system logical volumes which are not CD-ROM, without drive letter or with size attribute equal to 0
$volumes = (Get-Volume |
    Where-Object {$_.DriveLetter -ne $Null} | 
    Where-Object {$_.DriveType -ne "CD-ROM"} |
    Where-Object {$_.Size -ne 0})

# Get required information for every volume
foreach ($volume in $volumes){
    $device = $Volume.DriveLetter + ":" + $Volume.FileSystemLabel # Drive letter and label
    $size = [math]::floor($Volume.Size/$MB) # Rounded drive size in MB
    $free = [math]::floor($Volume.SizeRemaining/$MB) # Rounded free drive space in MB
    # From gathered information determine storage device state (alert, warning, normal)
    if ($free -le $ALERT) 
        {$state="alert"} 
    elseif ($free -le $WARNING) 
        {$state="warning"}
    else 
        {$state="normal"}

    # Calculate drive usage in percents
    $used_perc = [math]::floor(($size-$free)*100/$size)

    # Form API request from hostname and drive name. If device ID not found - create record, else - update values
    $REQ_URI = $URI + "?host=" + $hostname + "&device=" + $device
    
    # Try to get response from request
    try {
        # If device exists, read ID and update values with put method
        $response = Invoke-RestMethod -Method 'Get' -Uri $REQ_URI -ContentType 'application/json'
        
        $params = @{
            id = $response.id
            state = $state
            size_mb = $size
            free_mb = $free
            used_perc = $used_perc
            }

        if (!$QUIET){
            Write-Host "Device" $device "exists with id:" $response.id "Updating..."
            # Put new data for existing device
            Invoke-RestMethod -Method 'Put' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" | ConvertTo-Json
        }
        else{
            # Put new data for existing device
            Invoke-RestMethod -Method 'Put' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" >$null 2>&1
        }       
    } catch {
        # If response returns 404 (device doesnt exist), create device with post method
        $params = @{
            host = $hostname
            device = $device
            state = $state
            size_mb = $size
            free_mb = $free
            used_perc = $used_perc
            }

        if (!$QUIET){
            Write-Host "Device" $device "doesnt exist. Creating..."
            # Post new device data
            Invoke-RestMethod -Method 'Post' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" >$null 2>&1
        }
        else {
            # Post new device data    
            Invoke-RestMethod -Method 'Post' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" | ConvertTo-Json
        }
        }
    }
