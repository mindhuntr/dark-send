from dark_send.meta_data import meta_extract
from dark_send.inquirer import display_list
from dark_send.progress_bar import progress
from argparse import ArgumentParser
from os import path
import subprocess
import asyncio 
import socket
import json 
import sys


""" Get api id and hash from https://my.telegram.org """

SOCK_PATH = "/tmp/dark-send.sock" 
CONFIG_DIR = "~/.config/dark-send/"
HEADER = 4096

class DarkSendSocket:
    def __init__(self, path):
        self.path = path
        self.sock = None

    def __enter__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(self.path)
        return self

    def start_server(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(SOCK_PATH)
        self.sock.listen(5)

    def relay_to_server(self, cmd_dict):
        message = json.dumps(cmd_dict).encode('utf-8') 
        message_length = len(message) 

        header_message = str(message_length).encode('utf-8')
        header_message += b' ' * (HEADER - len(header_message)) 

        self.sock.send(header_message)
        self.sock.send(message)

    def get_from_server(self): 
        message_length = self.sock.recv(HEADER).decode('utf-8') 
        message = self.sock.recv(int(message_length)).decode('utf-8') 
        return message 

    def relay_to_client(self, conn, cmd_dict):

        message = json.dumps(cmd_dict).encode('utf-8') 
        message_length = len(message) 

        header_message = str(message_length).encode('utf-8')
        header_message += b' ' * (HEADER - len(header_message)) 

        conn.send(header_message)
        conn.send(message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

async def cli(args):

    async def reload_chats(): 

        nonlocal chat_list 
        with DarkSendSocket(SOCK_PATH) as sock:
            cmd = [{"client": "user", "type": "get_chats"}]
            sock.relay_to_server(cmd) 
            response = sock.get_from_server() 

        chat_list = json.loads(response) 

        with open(chat_path, 'w') as chat_file: 
            json.dump(chat_list, chat_file) 

    async def load_chats(): 
        nonlocal chat_list
        with open(chat_path, 'r') as chat_file: 
            chat_list = json.load(chat_file) 

    def display_progress(album, files, chats, colour): 

        count = len(files) * len(chats) if not album else len(chats)
        for i in range(0, count):
            while True:
                data = sock.get_from_server() 

                for line in data.splitlines():
                    msg = json.loads(line)
                    current = msg["current"]
                    total = msg["total"]
                    progress(current, total, colour) 

                if current == total:
                    break

    async def display_dialog():
        nonlocal chats
        nonlocal chat_list

        if args.chats: 
            for chat in args.chats: 
                if not chat in chat_list: 
                    print(f"Chat \"{chat}\" not found") 
                    exit(1)

        chat_list = dict(list(chat_list.items())[:args.nchats])
        chats = await display_list(args.chats, chat_list)  # Display chat list


    # Send Message
    async def send_message(sock, chats, messages):
        cmd_arr = [] 
        for message in messages:
            for chat in chats:
                cmd = {"client": client, "type": "send_message", "chat": chat[0], "text": message, "reply_to": chat[1]}
                cmd_arr.append(cmd)
                
        sock.relay_to_server(cmd_arr) 

    # Send Videos
    async def send_videos(sock, chats, videos):
        cmd_arr = [] 
        if not args.album:
            for video in videos:
                if path.exists(video):
                    height, width, duration = meta_extract(video)
                    for chat in chats:
                        cmd = {
                            "client": client,
                            "type": "send_video", "chat": chat[0], 
                            "video": path.abspath(video), "caption": args.caption[0], 
                            "reply_to": chat[1],
                            "height": height, "width": width, "duration": duration,
                            "quiet": args.quiet,
                            "album": "no"
                        }
                        cmd_arr.append(cmd)
                else:
                    print(f"{video} doesnt exist")
                    return 1
        else:
            for chat in chats:
                video_paths = [ path.abspath(video) for video in videos ]  # Send videos as album
                cmd = {
                    "client": client,
                    "type": "send_video", "chat": chat[0], 
                    "video": video_paths, "caption": args.caption[0], 
                    "reply_to": chat[1],
                    "quiet": args.quiet,
                    "album": "yes"
                }
                cmd_arr.append(cmd)

        sock.relay_to_server(cmd_arr) 
        if not args.quiet:
            display_progress(args.album, videos, chats, args.progress_colour) 

    # Send Images
    async def send_images(sock, chats, images):
        cmd_arr = [] 
        if not args.album:
            for image in images:
                if path.exists(image):
                    for chat in chats:
                        cmd = {
                            "client": client,
                            "type": "send_image", "chat": chat[0], 
                            "image": path.abspath(image), "caption": args.caption[0], 
                            "reply_to": chat[1], "quiet": args.quiet 
                        }

                        cmd_arr.append(cmd)
                else:
                    print("{} doesnt exist".format(image))
                    return 1
        else:                                                           
            for chat in chats:
                image_paths = [ path.abspath(image) for image in images ]  # Send images as album
                cmd = {
                    "client": client,
                    "type": "send_image", "chat": chat[0], 
                    "image": image_paths, "caption": args.caption[0], 
                    "reply_to": chat[1], "quiet": args.quiet
                }
                cmd_arr.append(cmd)

        sock.relay_to_server(cmd_arr) 
        if not args.quiet:
            display_progress(args.album, images, chats, args.progress_colour) 

    # Send files
    async def send_files(sock, chats, files):
        cmd_arr = []
        if not args.album:
            for file in files:
                if path.exists(file):
                    for chat in chats:
                        cmd = {
                            "client": client,
                            "type": "send_file", "chat": chat[0], 
                            "file": path.abspath(file), "caption": args.caption[0], 
                            "reply_to": chat[1], "quiet": args.quiet
                        }
                        cmd_arr.append(cmd)
                else:
                    print("{} doesnt exist".format(file))
                    return 1

        else:
            files_album = []
            for file in files:
                if path.exists(file):
                    files_album.append(path.abspath(file))
                else:
                    print("{} doesnt exist".format(file))
                    return 1

            if files_album:
                for chat in chats:
                    cmd = {
                        "client": client,
                        "type": "send_file", "chat": chat[0], 
                        "file": files_album, "caption": args.caption[0], 
                        "reply_to": chat[1], "quiet": args.quiet
                    }
                    cmd_arr.append(cmd)

        sock.relay_to_server(cmd_arr) 
        if not args.quiet:
            display_progress(args.album, files, chats, args.progress_colour) 

    async def get_bots(sock): 

        cmd = [{"client": "user", "type": "get_bots"}]
        sock.relay_to_server(cmd) 
        response = sock.get_from_server() 

        bot_list = json.loads(response)

        for bot in bot_list.values(): 
            print(bot) 


    chat_path = path.join(path.dirname(path.expanduser(CONFIG_DIR)), "chats.json")
    chats = []
    chat_list = {}

    if path.exists(chat_path) and not args.refresh: 
        await load_chats() 
    else: 
        await reload_chats() 
        print("Refreshed local chat store")
        exit()

    args.caption = args.caption or [None]
    client = args.bot_name or "user"

    if args.message:
        await display_dialog()
        with DarkSendSocket(SOCK_PATH) as sock:
            await send_message(sock, chats, args.message)

    if args.image:
        await display_dialog()
        with DarkSendSocket(SOCK_PATH) as sock:
            await send_images(sock, chats, args.image)

    if args.video:
        await display_dialog()
        with DarkSendSocket(SOCK_PATH) as sock:
            await send_videos(sock, chats, args.video)

    if args.file:
        await display_dialog()
        with DarkSendSocket(SOCK_PATH) as sock:
            await send_files(sock, chats, args.file)

    if args.list_bots: 
        with DarkSendSocket(SOCK_PATH) as sock:
            await get_bots(sock)

async def main():

    parser = ArgumentParser(description='command line telegram client')
    parser.add_argument('message', type=str, help="the message you would like to send", nargs="*")
    parser.add_argument("--daemonize", action="store_true", help="run in daemon mode")
    parser.add_argument('-v', '--video', type=str, nargs="+", help="videos to send")
    parser.add_argument('-i', '--image', type=str, nargs="+", help="images to send")
    parser.add_argument('-f', '--file', type=str, nargs="+", help="files to send")
    parser.add_argument('-n', '--nchats', type=int, nargs="?", default=100, help="no chats to display")
    parser.add_argument('-c', '--chats', type=str, nargs="*", help="name of the chat")
    parser.add_argument('-t', '--caption', type=str, nargs="*", help="caption for file")
    parser.add_argument('-a', '--album', action="store_true", help="send files as albums")
    parser.add_argument('-q', '--quiet', action="store_true", help="suppress progress bar")
    parser.add_argument('-r', '--refresh', action="store_true", help="refresh local chat store")
    parser.add_argument('-p', '--progress-colour', type=str, default="#b4befe", help="progress bar color in hex format (e.g. #RRGGBB)")
    parser.add_argument('--initialize-bot', action="store_true", help="initialize bot account") 
    parser.add_argument('--list-bots', action="store_true", help="list bot accounts") 
    parser.add_argument('-b', '--bot-name', type=str, nargs="?", help="use bot account instead of user") 

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    if not path.exists(path.join(path.expanduser(CONFIG_DIR) + "dark-send.conf")):
        import dark_send.config as config
        await config.generate_userconf()

    if args.initialize_bot: 
        import dark_send.config as config
        await config.generate_botconf()

    if args.daemonize:
        subprocess.Popen(
            [sys.executable, "-m", "dark_send.daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        print("Daemon started in background")
        sys.exit(0)
    else:
        try:
            await cli(args)
        except (ConnectionRefusedError, FileNotFoundError) as e: 
            print(f"Caught error {e}") 
            print("Daemonize the process using --daemonize to initialize socket") 

def entrypoint():
    asyncio.run(main())

if __name__ == "__main__":
    entrypoint() 
