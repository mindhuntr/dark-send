# dark-send 

A relatively simple command line telegram client written in python 

## Installation 
``` shell
git clone https://github.com/mindhuntr/dark-send 
``` 

## Usage 

Display help: 
``` shell 
dark --help 
``` 

To send a message:
``` shell
dark "Hello!" 
``` 

To send a file: 
``` shell 
dark -f /path/to/file 
``` 

To send files as album: 
``` shell 
dark -a -f /path/to/file /path/to/file 
``` 

To send a video: 
``` shell 
dark -v /path/to/file 
``` 

To send a file directly without selecting from the list
``` shell 
dark -f /path/to/file -c "name_of_the_chat" 
```

