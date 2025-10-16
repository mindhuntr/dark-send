# dark-send 

Dark-send is a CLI telegram client written in python. It sends messages and files through your personal telegram account using a daemon that maintains a connection in the background, much like the stock telegram desktop app.

## Dependencies 

``` shell 
pip3 install -r requirements.txt 
``` 

## Installation 

Install directly from PyPi
```shell 
pip3 install dark-send 
```

Or 

Clone the repository to a local directory
``` shell
git clone https://github.com/mindhuntr/dark-send 
```

For system wide installation 
```shell
python3 setup.py install
```

For user specific installation 
```shell
python3 setup.py install --user 
```


## Configuration

dark-send requires a daemon process running in the background. The daemon can be initialized using a parameter 

```shell
dark-send --daemonize
```

Once the config file is generated, it is more robust to create a systemd-unit file that automatically executes the daemon once the system is up 

```

[Unit]
Description=Daemon for dark-send
After=network.target

[Service]
Type=simple
User=YOUR_USER
ExecStart=/usr/bin/python3 -m dark_send.daemon
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create a file called dark-send.service with the above content and place it in "/etc/systemd/system". Replace "YOUR_USER" with your username and execute the following commands

```shell
systemctl daemon-reload 
systemctl enable dark-send.service
systemctl start dark-send.service
```


## Usage 

Display help: 
``` shell 
dark-send --help 

``` 
To send a message:
``` shell
dark-send Hello!
``` 

![Demo](https://raw.githubusercontent.com/mindhuntr/dark-send/refs/heads/master/demos/send.gif)

To send an image: 
``` shell 
dark-send -i /path/to/image 

``` 
To send files as album: 
``` shell 
dark-send -a -f /path/to/file /path/to/file 
``` 

![Demo](https://raw.githubusercontent.com/mindhuntr/dark-send/refs/heads/master/demos/send_file.gif)

To send a video directly without selecting from the chats list
``` shell 
dark-send -v /path/to/file -c "Alienists" 
```
You can also send messages or files to topics within a group 

![Demo](https://raw.githubusercontent.com/mindhuntr/dark-send/refs/heads/master/demos/send_topic.gif)

## Note 

dark-send now supports bot logins from v1.2.0. It leverages the user client to fetch chats and then the bot account to send messages and files. Users can initialize several bot accounts and use them by names they designate. 

```shell 
dark-send -b FelineBot -f /path/to/file 
```
