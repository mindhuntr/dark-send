# dark-send 

A relatively simple command line telegram client written in python 

## Dependencies 
``` shell 
pip3 install -r requirements.txt 
``` 

## Installation 
``` shell
git clone https://github.com/mindhuntr/dark-send 
``` 

## Usage 

Display help: 
``` shell 
dark-send --help 
``` 
To send a message:
``` shell
dark-send "hello" 
``` 
![Demo](./demos/send.gif)

To send a file: 
``` shell 
dark-send -f /path/to/file 

``` 
To send files as album: 
``` shell 
dark-send -a -f /path/to/file /path/to/file 
``` 
![Demo](./demos/send_file.gif)

To send a file directly without selecting from the list
``` shell 
dark-send -f /path/to/file -c "Alienists" 
```
You can also send messages or files to topics within a group 

![Demo](./demos/send_topic.gif)

