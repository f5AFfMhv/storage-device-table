# What is SDT?
Storage Device Table is monitoring solution containing RESTful API and web application. Application is written in python3 and is based on Flask module.  
Web application is refreshed every minute. Pressing on server hostname generates plotly bar graph with servers storage information.  
All data from internal database can be exported to CSV file.

<div align="center">
    <img src="https://i.imgur.com/Fyjmb0A.gif" width="100%" alt="api"/>
</div>

# Installation
1. Clone repository.
````
cd /opt
git clone https://github.com/f5AFfMhv/storage-device-table.git
cd storage-device-table/
````
2. Install requirements (`python3` and `pip` should be installed from your system repositories).
````
pip3 install -r requirements.txt
````
3. Make `app.py` executable.
````
chmod +x app.py
````
4. Open port in firewall. In case of `firewalld` run these commands.
````
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
````
5. Run `app.py` to start server. To create service for `systemd` create `/etc/systemd/system/sdt.service` file.
````
[Unit]
Description=Storage device usage monitor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/storage-device-table
ExecStart=/opt/storage-device-table/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
````
6. Start and enable service.
````
systemctl daemon-reload
systemctl enable sdt
systemctl start sdt
````

# Docker
Run docker container.
````
docker run -d -p 5000:5000 f5affmhv/storage-device-table
````
Or build image from Dockerfile
````
git clone https://github.com/f5AFfMhv/storage-device-table.git
cd storage-device-table/
docker build -t storage-device-table .
````

# API
SDT data internally is saved in SQLite database. Clients post data about each device individually.  
Data contains information about server hostname, drive mount point, device total size in MB, free space in MB, device usage in percentage and status. Additionally application saves server IP address and record update time to database. Each storage device is assigned unique ID by database itself. For more information on API functionality check project wiki page.

# Agents
Currently there are 3 agents for posting and updating data with SDT API.  

## SDT-linux-agent.sh
Script gathers system information about main storage devices with `df` tool. Then it tries to find each device in database, if device exist JSON file is formed with new values and existing record is updated. If device isn't found, new record is created in the database.  
Default values defined at the beginning of a script, values can be overwritten by passing them as parameters when executing script. For example:  
````
./SDT-linux-agent.sh -s 192.168.100.100 -a 90 -w 80
````
will determine device state with thresholds: >90% drive usage - alert, >80% drive usage - warning and will try to post it to application running on 192.168.100.100. Script has a dependency on `jq` - command-line JSON processor, which can be installed from default repositories.  
For more information execute this command.
````
./SDT-linux-agent.sh -h
````
## SDT-ansible-playbook.yml
This ansible playbook will gather information from hosts about their storage devices and check if SDT server is reachable. Then for each device it will check if device exists in database and depending on the result, will update or create new record. Parameters can be modified in playbooks `vars` section.  
````
ansible-playbook SDT-ansible-playbook.yml
````
## SDT-windows-agent.ps1
Windows agent working principle is identical to linux shell script. To post data about drives to SDT API on server 192.168.100.100 with alert usage threshold of 90% and warning threshold of 80% execute script as follows:
````
.\SDT-windows-agent.ps1 -s 192.168.100.100 -a 90 -w 80
````
Additionally when `-ad` flag is passed, instead of checking only local drives, all computers from Active Directory will be queried. For this to work:
* RSAT on client machine should be installed;
* script should be executed by AD user which have sufficient permissions to query AD hosts;
* on each host remote query should be allowed.
````
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
````
To get help execute:
````
Get-Help .\SDT-windows-agent.ps1 -Full
````