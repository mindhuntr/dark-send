from telethon.tl.types import DocumentAttributeVideo, InputMessagesFilterPhotos, InputMessagesFilterMusic
from telethon.tl.types import InputMessagesFilterVideo, InputMessagesFilterDocument
from telethon.tl.functions.channels import GetForumTopicsRequest
from telethon.sessions import StringSession
from telethon import TelegramClient, utils
import dark_send.config as config
from datetime import datetime
from os import path, remove
import mimetypes
import socket
import json 

SOCK_PATH = "/tmp/dark-send.sock" 

async def daemonize(): 

    if path.exists(config.fullpath):
        config.parser.read(config.fullpath)
        api_id = int(config.parser.get('dark-send', 'api_id'))
        api_hash = config.parser.get('dark-send', 'api_hash')
        string = config.parser.get('dark-send', 'string_session')

    else:
        print(f"Config file at {config.fullpath} does not exist")
        return 1

    client = TelegramClient(StringSession(string), api_id, api_hash)
    await client.start()

    # clean up old socket
    if path.exists(SOCK_PATH):
        remove(SOCK_PATH)

    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCK_PATH)
    server.listen(5)

    print(f"Socket binded at {SOCK_PATH}") 

    def upload_progress(current, total):
        update = json.dumps({"type": "progress", "current": current, "total": total})
        conn.send(update.encode())


    sock_buf = ""

    while True:
        conn, _ = server.accept()
        cmd_arr = []

        while True:
            sock_buf += conn.recv(4096).decode() 

            while "\n" in sock_buf: 
                line, sock_buf = sock_buf.split("\n", 1)
                if not line.strip(): 
                    continue 

                cmd = json.loads(line) 
                if cmd["type"] == "end": 
                    break 
                cmd_arr.append(cmd) 

            if cmd_arr and cmd["type"] == "end":
                break
        try:
            for cmd in cmd_arr:
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

                elif cmd["type"] == "get_chats":
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

                    conn.sendall((json.dumps(chat_list) + "\n").encode()) 

                else:
                    conn.send(b"unknown command")

        except Exception as e:
            conn.send(str(e).encode())
        finally:
            sock_buf = ""
            conn.close() 

