from telethon.sessions import StringSession
from telethon.sync import TelegramClient
import configparser 
import os 

parser = configparser.ConfigParser() 
fullpath = os.path.expanduser("~/.config/dark-send/dark-send.conf") 

async def generate_conf():
    
    print("Get api id and hash from https://my.telegram.org") 

    api_id = input("Enter your api id: ").strip()
    api_hash = input("Enter your api hash: ").strip()
    phone = input("Enter your phone number (include country code, e.g. +1415555267): ").strip()

    string_session = ''

    if api_id and api_hash and phone:

        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.start(phone)

        string_session = client.session.save()

        parser['dark-send'] = {
                'api_id': api_id,
                'api_hash': api_hash, 
                'string_session': string_session
                } 

        os.makedirs(os.path.dirname(fullpath), exist_ok=True) 

        with open(fullpath, 'w') as f: 
            parser.write(f) 
