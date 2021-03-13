<#
.SYNOPSIS
.DESCRIPTION
    This is linux agent for storage device monitoring application. For more information check https://github.com/f5AFfMhv
.EXAMPLE
    C:\PS> .\SDT-windows-agent.ps1 -s 192.168.100.100 -a 90 -w 80  
    Post drive information to server 192.168.100.100 with usage alert threshold of 90%
    and warning threshold of 80%.
#>

param (
    # Server IP/FQDN
    [string]$s="192.168.0.2",
    # Threshold usage in percents for device status WARNING
    [int]$w=70,
    # Threshold usage in percents for device status ALERT             
    [int]$a=90,
    # Quiet stdout                
    [switch]$q
    )
    
# API url
$URI = "http://" + $s + ":5000/api/v1/devices"
# Byte value for disk size conversion to MB
$MB=1048576 # 1 MB = 1048576 B
# Determine server name
$hostname = (Get-CimInstance -ClassName Win32_ComputerSystem).name
# Server timeout in seconds
$server_timeout_sec = 5

# Check server availability
$check_url = "http://" + $s + ":5000"
try {
    Invoke-RestMethod $check_url -TimeoutSec $server_timeout_sec >$null 2>&1
} catch {
    Write-Host "Server unavailable"
    Exit
}

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
    # Calculate drive usage in percents
    $used_perc = [math]::floor(($size-$free)*100/$size)

    # From gathered information determine storage device state (alert, warning, normal)
    if ($used_perc -ge $a) 
        {$state="alert"} 
    elseif ($used_perc -ge $w) 
        {$state="warning"}
    else 
        {$state="normal"}

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

        if (!$q){
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

        if (!$q){
            Write-Host "Device" $device "doesnt exist. Creating..."
            # Post new device data
            Invoke-RestMethod -Method 'Post' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" | ConvertTo-Json
        }
        else {
            # Post new device data    
            Invoke-RestMethod -Method 'Post' -Uri $URI -Body ($params|ConvertTo-Json) -ContentType "application/json" >$null 2>&1
        }
        }
    }
