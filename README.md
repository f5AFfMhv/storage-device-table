# What is SDT?
Storage Device Table is monitoring solution containing RESTful API and web application. Application is writen in python3 and is based on Flask module.  
Web application is refreshed every minute. Pressing on server hostname generates plotly bargraph with that server storage information in GB.  
All data from internal database can be exported to CSV file.

<div align="center">
    <img src="https://i.imgur.com/UIilfT7.gif" width="100%" alt="api"/>
</div>

# Installation
1. Clone repository
````
cd /opt
git clone http://localhost:3000/mint/disk_monitor.git
cd disk_monitor/
````
2. Install requirements (`python3` and `pip` should be installed from your system repositories)
````
pip3 install -r requirements.txt
````
3. Make `app.py` executable
````
chmod +x app.py
````
4. Open port in firewall. In case of `firewalld` run these commands
````
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
````
5. Run `app.py` to start server. To create service for `systemd` create `/etc/systemd/system/sdt.service` file containing
````
[Unit]
Description=Server device usage application service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/disk_monitor
ExecStart=/opt/disk_monitor/app.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
````
6. Start service and configure it to start automaticaly at system startup
````
systemctl daemon-reload
systemctl enable sdt
systemctl start sdt
````

# API
SDT data internaly is saved in SQLite database. Clients post data about each device individualy.  
Data contains information about server hostname, drive mount point, device total size in MB, free space in MB, device usage in percentage. Aditionaly application saves server IP address and update time to database. Each storage device is asigne unique ID by database itself. For more information on API functionality check project wiki page.

<div align="center">
    <img src="https://i.imgur.com/QCW8o3Y.gif" width="80%" alt="api"/>
</div>

# Agents
Curently there are 3 agents for posting and updating data with SDT API.  
## SDT-linux-agent.sh
Script gathers system information about main storage devices with `df` tool. Then it tries to find each device in database, if device exist JSON file is formed with new values and existing record is updated. Else new record is created in the database.  
Default variables defined at the beginning of script. Also parameters can be overwriten by passing them as parameters when executing script. For example:  
````
./SDT-linux-agent.sh -s 192.168.100.100 -a 90 -w 80
````
will determine device state with thresholds: >90% usage - alert, >80% usage - warning and will try to post it to 192.168.100.100.  
For more information execute 
````
./SDT-linux-agent.sh -h
````
## SDT-ansible-playbook.sh
This ansible playbook will gather information from hosts about their storage devices. Then it will check if SDT server is reachable. Then for each device it will check if device exists in database and depending on the result, will update or create record. Parameters can be modified in playbooks `vars` section.
````
ansible-playbook SDT-ansible-playbook.yml
````
## SDT-windows-agent.ps1
Windows agent is powershell script. Its working principle is identical to linux shell script. To post data about drives to SDT API on server 192.168.100.100 with alert usage threshold of 90% and warning threshold of 80% execute script as follows:
````
.\SDT-windows-agent.ps1 -s 192.168.100.100 -a 90 -w 80
````
Aditionaly when `-ad` flag is passed, insted of checking only local drives, all computers from Active Directory will be queried. For this to work script should be executed by AD user which have sufient permmisions to query AD hosts. Also on each host this command should be run to allow remote query:
````
netsh advfirewall firewall set rule group="Windows Management Instrumentation (WMI)" new enable=yes
````
To get help execute:
````
Get-Help .\SDT-windows-agent.ps1 -Full
````