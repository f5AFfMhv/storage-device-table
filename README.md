# What is SDT?
Storage Device Table is monitoring solution containing RESTful API and web application. Application is writen in python3 and is based on Flask module.  
Web application is refreshed every minute. Pressing on server hostname generates plotly bargraph with that server storage information in GB.  
All data from internal database can be exported to CSV file.

<div align="center">
    <img src="https://i.imgur.com/UIilfT7.gif" width="100%" alt="api"/>
</div>

# API
SDT data internaly is saved in SQLite database. Clients post data about each device individualy.  
Data contains information about server hostname, drive mount point, device total size in MB, free space in MB, device usage in percentage. Aditionaly application saves server IP address and update time to database. Each storage device is asigne unique ID by database itself. For more information on API functionality check project wiki page.

<div align="center">
    <img src="https://i.imgur.com/QCW8o3Y.gif" width="100%" alt="api"/>
</div>

# Agents

Curently there are 3 agents for posting and updating data with SDT API.  
## SDT-linux-agent.sh
Script 
# Install

## Requirements
## Agents
Script gathers system information about main storage devices, forms JSON file and posts it to SDT API.  
Default variables defined at the beginning of script. Also parameters can be overwriten by passing them as parameters when executing script. For example:  
````
    ./SDT-linux-agent.sh -q -s 192.168.100.100 -a 90 -w 80
````
will 

# Docker