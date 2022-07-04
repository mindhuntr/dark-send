import sys
import os 
import configparser 
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

parser = configparser.ConfigParser() 
fullpath = os.path.expanduser("~/.config/dark-send.conf") 

def generate_conf():
    
    print("Get api id and hash from https://my.telegram.org") 

    api_id = input("Enter your api id: ") 
    api_hash = input("Enter your api hash: ") 
    string_session = ''

    if api_id and api_hash:

        with TelegramClient(StringSession(),api_id,api_hash) as client: 
            string_session = client.session.save() 

        parser['dark-send'] = {
                'api_id': api_id,
                'api_hash': api_hash, 
                'string_session': string_session
                } 

        with open(fullpath, 'w') as f: 
            parser.write(f) 
