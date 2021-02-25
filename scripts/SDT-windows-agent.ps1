
# Script gathers system information about main storage devices,
# forms JSON request and posts it to SDT API

# Main variables
# Server IP or resolvable fqdn
$SERVER="192.168.0.2"
# API url
$URI = "http://" + $SERVER + ":5000/api/v1/resources/servers"
# Threshold values of free space in GB to determine device state
$ALERT=5 # If device has less free space in GB than this value, device will be assignet alert state
$WARNING=25 # If device has less free space in GB than this value, device will be assignet warning state
# Flag for QUIET mode
$QUIET=$false
# Byte value for disk size conversion to GB
$GB=1073741824 # 1 GB = 1073741824 B
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

# Determine server name
$name = (Get-CimInstance -ClassName Win32_ComputerSystem).name

# Get information on system logical volumes which are not CD-ROM, without drive letter or with size attribute equal to 0
$volumes = (Get-Volume |
    Where-Object {$_.DriveLetter -ne $Null} | 
    Where-Object {$_.DriveType -ne "CD-ROM"} |
    Where-Object {$_.Size -ne 0})

# For every storage device in list, get information about it
foreach ($volume in $volumes){
    $device = $Volume.DriveLetter + ":" + $Volume.FileSystemLabel # Drive letter and label
    $size = [math]::floor($Volume.Size/$GB) # Rounded drive size in GB
    $free = [math]::floor($Volume.SizeRemaining/$GB) # Rounded free drive space in GB
    # From gathered information determine storage device state (alert, warning, normal)
    if ($free -le $ALERT) 
        {$state="alert"} 
    elseif ($free -le $WARNING) 
        {$state="warning"}
    else 
        {$state="normal"}

    # Calculate drive usage in percents
    $used_perc = [math]::floor(($size-$free)*100/$size)

    if (!$QUIET){
        Write-Host $device "size:" $size ", free:" $free ", usage:" $used_perc ", state:" $state
    }

    # From API request device from hostname and drive. If device ID not found - create record, else - update values
    $REQ_URI = $URI + "?name=" + $name + "&device=" + $device
    
    # Try to get response from request
    try {
        # If device exists, read ID and update values with put method
        $response = Invoke-RestMethod -Method 'Get' -Uri $REQ_URI -ContentType 'application/json'
        $params = @{
            id = $response.id
            state = $state
            size_gb = $size
            free_gb = $free
            used_perc = $used_perc
            }
            Invoke-RestMethod -Method 'Put' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json"
    } catch {
        # If response returns 404, create device with post method
        $params = @{
            name = $name
            device = $device
            state = $state
            size_gb = $size
            free_gb = $free
            used_perc = $used_perc
            }
        Invoke-RestMethod -Method 'Post' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json"
        }
    }
