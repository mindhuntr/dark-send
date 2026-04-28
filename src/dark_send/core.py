from telethon.tl.functions.messages import GetForumTopicsRequest, GetPeerDialogsRequest, GetForumTopicsByIDRequest
from dark_send.concurrent_upload import TelegramUploadClient
from telethon.tl.types import DocumentAttributeVideo
from telethon.sessions import StringSession
from dark_send.cli import DarkSendSocket
import dark_send.config as config
from datetime import datetime
from os import path, remove
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

    user_client = TelegramUploadClient(StringSession(string), api_id, api_hash)
    await user_client.start()

    bot_sessions = {} 
    bot_sections = [ s for s in config.parser.sections() if s != 'dark-send' ]

    for section in bot_sections: 
        string_session = config.parser.get(section, 'string_session')
        bot_sessions[section] = TelegramUploadClient(StringSession(string_session), api_id, api_hash)
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

                match cmd["type"]: 
                    case "send_message":
                        await client.send_message(cmd["chat"], cmd["text"], reply_to=cmd["reply_to"])

                    case "send_image": 
                        if cmd["album"] == "no":
                            if cmd["quiet"] == False: 
                                image_handle = await client.upload_file(
                                    cmd["image"],
                                    progress_callback=upload_progress,
                                    part_size_kb=512)
                            else: 
                                image_handle = await client.upload_file(
                                    cmd["image"],
                                    part_size_kb=512)

                            for chat in cmd["chats"]:
                                await client.send_file( 
                                    chat[0], image_handle,
                                    reply_to=chat[1], caption=cmd["caption"],
                                    ) 

                        else: 
                            img_arr = []
                            for image in cmd["image"]:
                                if cmd["quiet"] == False: 
                                    image_handle = await client.upload_file(
                                        image,
                                        progress_callback=upload_progress,
                                        part_size_kb=512)
                                else: 
                                    image_handle = await client.upload_file(
                                        image,
                                        part_size_kb=512)

                                img_arr.append(image_handle)

                            for chat in cmd["chats"]:
                                await client.send_file(
                                    chat[0], img_arr,
                                    reply_to=chat[1], 
                                    caption=cmd["caption"]
                                )

                    case "send_video":
                        if cmd["album"] == "no":
                            if cmd["quiet"] == False:
                                video_handle = await client.upload_file(
                                    cmd["video"],
                                    progress_callback=upload_progress,
                                    part_size_kb=512)
                            else: 
                                video_handle = await client.upload_file(
                                    cmd["video"],
                                    part_size_kb=512
                                )

                            for chat in cmd["chats"]:
                                await client.send_file(
                                    chat[0], video_handle,
                                    video=True, attributes=(DocumentAttributeVideo(cmd["duration"], cmd["width"], cmd["height"], supports_streaming=True),),
                                    reply_to=chat[1], caption=cmd["caption"]
                                    )
                        else:
                            video_arr = []
                            for video in cmd["video"]:
                                if cmd["quiet"] == False:
                                    video_handle = await client.upload_file(
                                        video,
                                        progress_callback=upload_progress,
                                        part_size_kb=512)
                                else: 
                                    video_handle = await client.upload_file(
                                        video,
                                        part_size_kb=512
                                    )
                                video_arr.append(video_handle) 

                            for chat in cmd["chats"]:
                                await client.send_file(
                                    chat[0], video_arr,
                                    video=True,reply_to=chat[1], 
                                    caption=cmd["caption"]
                                )


                    case "send_file": 
                        if cmd["album"] == "no":
                            if cmd["quiet"] == False:
                                file_handle = await client.upload_file(
                                    file=cmd["file"],
                                    file_name=cmd["file"], 
                                    progress_callback=upload_progress,
                                )
                            else: 
                                file_handle = await client.upload_file(
                                    file=cmd["file"],
                                    file_name=cmd["file"], 
                                )

                            for chat in cmd["chats"]:
                                await client.send_file( 
                                    chat[0], file_handle, 
                                    force_document=True,
                                    reply_to=chat[1],
                                    caption=cmd["caption"]
                                ) 
                        else: 
                            file_arr = [] 
                            for file in cmd["file"]: 
                                if cmd["quiet"] == False:
                                    file_handle = await client.upload_file(
                                        file=file,
                                        file_name=file, 
                                        progress_callback=upload_progress,
                                    )
                                    file_arr.append(file_handle)
                                else: 
                                    file_handle = await client.upload_file(
                                        file=file,
                                        file_name=file, 
                                    )
                                    file_arr.append(file_handle)

                            for chat in cmd["chats"]:
                                await client.send_file( 
                                    chat[0], file_arr, 
                                    force_document=True,
                                    reply_to=chat[1],
                                    caption=cmd["caption"]
                                ) 

                    case "get_chats": 
                        if cmd["client"] == "user":
                            chat_list = {}
                            async for dialog in client.iter_dialogs(100):
                                if hasattr(dialog.entity, "deactivated"): 
                                    if dialog.entity.deactivated: 
                                        continue

                                if not hasattr(dialog.entity, "forum"):
                                    chat_list[dialog.name] = dialog.id
                                else:
                                    if dialog.entity.forum:
                                        topic_obj = await client(GetForumTopicsRequest(
                                            peer=dialog.id, offset_date=datetime.now(),
                                            offset_id=1, offset_topic=1, limit=100))

                                        topics = [{topic.title: topic.id} for topic in topic_obj.topics]
                                        chat_list[dialog.name] = [dialog.id, topics]
                                    else:
                                        chat_list[dialog.name] = dialog.id

                            server.relay_to_client(conn, chat_list) 

                    case "get_bots": 
                        bot_list = {}
                        for index, section in enumerate(bot_sections, start=1):
                            bot_list[index] = section 

                        server.relay_to_client(conn, bot_list) 

                    case "unread_messages": 
                        all_messages = {} 

                        for chat in cmd["chats"]:
                            entity = await client.get_entity(chat[0]) 

                            if chat[1]: 
                                result = await client(GetForumTopicsByIDRequest( 
                                    peer=chat[0], 
                                    topics=[chat[1]],
                                ))
                                unread_count = result.topics[0].unread_count
                            else:
                                result = await client(GetPeerDialogsRequest(
                                    peers=[entity]
                                ))
                                unread_count = result.dialogs[0].unread_count

                            messages = [] 
                            chat_name = entity.title if hasattr(entity, "title") else entity.first_name

                            if hasattr(entity, "title"):
                                user_mappings = {} 

                                async for message in client.iter_messages(entity,limit=unread_count, reply_to=chat[1]): 
                                    user_id = message.from_id.user_id

                                    if user_id not in user_mappings:
                                        entity = await client.get_entity(user_id)
                                        user_mappings[user_id] = entity.first_name

                                    messages.append({ user_mappings[user_id]: message.message })

                            else:
                                async for message in client.iter_messages(entity,limit=unread_count): 
                                    messages.append({ chat_name: message.message })

                            all_messages[chat_name] = messages

                        server.relay_to_client(conn, all_messages)

            except Exception as e:
                server.relay_to_client(conn, {"error": "query failed"})
                print(str(e)) 

        conn.close()
