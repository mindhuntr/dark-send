from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.tl.types import DocumentAttributeVideo
from telethon.sessions import StringSession
from telethon import TelegramClient, utils
from dark_send.cli import DarkSendSocket
import dark_send.config as config
from datetime import datetime
from os import path, remove
import mimetypes
import socket
import json 

SOCK_PATH = "/tmp/dark-send.sock" 
HEADER = 4096

async def daemonize(): 

    if path.exists(config.fullpath):
        config.parser.read(config.fullpath)
        api_id = int(config.parser.get('dark-send', 'api_id'))
        api_hash = config.parser.get('dark-send', 'api_hash')
        string = config.parser.get('dark-send', 'string_session')

    else:
        print(f"Config file at {config.fullpath} does not exist")
        return 1

    user_client = TelegramClient(StringSession(string), api_id, api_hash)
    await user_client.start()

    bot_sessions = {} 
    bot_sections = [ s for s in config.parser.sections() if s != 'dark-send' ]

    for section in bot_sections: 
        string_session = config.parser.get(section, 'string_session')
        bot_sessions[section] = TelegramClient(StringSession(string_session), api_id, api_hash)
        await bot_sessions[section].start()

    # clean up old socket
    if path.exists(SOCK_PATH):
        remove(SOCK_PATH)

    server = DarkSendSocket(SOCK_PATH)
    server.start_server() 

    print(f"Socket binded at {SOCK_PATH}") 

    def upload_progress(current, total):
        prog_dict = {"type": "progress", "current": current, "total": total}
        server.relay_to_client(conn, prog_dict) 

    while True:
        conn, _ = server.sock.accept()

        message_length = conn.recv(HEADER).decode('utf-8') 
        message = conn.recv(int(message_length)).decode('utf-8') 
        cmd_arr = json.loads(message) 

        for cmd in cmd_arr:
            try:
                if cmd["client"] == "user": 
                    client = user_client 
                else: 
                    bot_name = cmd["client"]
                    if bot_name in bot_sessions:
                        client = bot_sessions[bot_name] 
                    else: 
                        client = user_client 

                if cmd["type"] == "send_message":
                    await client.send_message(cmd["chat"], cmd["text"], reply_to=cmd["reply_to"])

                elif cmd["type"] == "send_image": 
                    if cmd["quiet"] == False: 
                        await client.send_file(
                            cmd["chat"], cmd["image"],
                            image=True,
                            part_size_kb=512, caption=cmd["caption"],
                            reply_to=cmd["reply_to"],
                            progress_callback=upload_progress
                                        )
                    else: 
                        await client.send_file(
                            cmd["chat"], cmd["image"],
                            image=True,
                            part_size_kb=512, caption=cmd["caption"],
                            reply_to=cmd["reply_to"],
                                        )

                elif cmd["type"] == "send_video":
                    if cmd["album"] == "no":
                        if cmd["quiet"] == False:
                            video_handle = await client.upload_file(
                                cmd["video"],
                                progress_callback=upload_progress,
                                part_size_kb=512)
                        else: 
                            video_handle = await client.upload_file(
                                cmd["video"],
                                part_size_kb=512)

                        await client.send_file(
                            cmd["chat"], video_handle,
                            video=True, attributes=(DocumentAttributeVideo(cmd["duration"], cmd["width"], cmd["height"], supports_streaming=True),),
                            reply_to=cmd["reply_to"], caption=cmd["caption"]
                            )
                    else:
                        if cmd["quiet"] == False:
                            await client.send_file(
                                cmd["chat"], cmd["video"],
                                video=True,
                                reply_to=cmd["reply_to"], caption=cmd["caption"],
                                progress_callback=upload_progress,
                                )
                        else:
                            await client.send_file(
                                cmd["chat"], cmd["video"],
                                video=True,
                                reply_to=cmd["reply_to"], caption=cmd["caption"],
                                )

                elif cmd["type"] == "send_file": 
                    if cmd["quiet"] == False:
                        await client.send_file(
                            cmd["chat"], cmd["file"],caption=cmd["caption"], 
                            reply_to=cmd["reply_to"], progress_callback=upload_progress, force_document=True
                        )
                    else: 
                        await client.send_file(
                            cmd["chat"], cmd["file"],caption=cmd["caption"], 
                            reply_to=cmd["reply_to"], force_document=True
                        )

                elif cmd["type"] == "get_chats" and cmd["client"] == "user":
                    chat_list = {}
                    async for dialog in client.iter_dialogs(100):
                        if not hasattr(dialog.entity, "forum"):
                            chat_list[dialog.name] = dialog.id
                        else:
                            if dialog.entity.forum:
                                topic_obj = await client(GetForumTopicsRequest(
                                    channel=dialog.id, offset_date=datetime.now(),
                                    offset_id=1, offset_topic=1, limit=100))

                                topics = [{topic.title: topic.id} for topic in topic_obj.topics]
                                chat_list[dialog.name] = [dialog.id, topics]
                            else:
                                chat_list[dialog.name] = dialog.id

                    server.relay_to_client(conn, chat_list) 

                elif cmd["type"] == "get_bots": 
                    bot_list = {}
                    for index, section in enumerate(bot_sections, start=1):
                        bot_list[index] = section 

                    server.relay_to_client(conn, bot_list) 

            except Exception as e:
                conn.send(str(e).encode())
        conn.close()

