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

async def cli(args):

    chats = []
    chat_list = {}
    chat_path = path.join(path.dirname(path.expanduser(CONFIG_DIR)), "chats.json")

    async def reload_chats(): 

        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SOCK_PATH)

        nonlocal chat_list 

        cmd = {"type": "get_chats"}
        sock.send((json.dumps(cmd) + "\n").encode())

        cmd = {"type": "end"} 
        sock.send((json.dumps(cmd) + "\n").encode())

        buf = "" 
        while True:
            data = sock.recv(4096).decode()
            buf += data
            if "\n" in buf: 
                break

        chat_list = json.loads(buf) 

        with open(chat_path, 'w') as chat_file: 
            json.dump(chat_list, chat_file) 

    async def load_chats(): 
        nonlocal chat_list
        with open(chat_path, 'r') as chat_file: 
            chat_list = json.load(chat_file) 

    def display_progress(album, files, chats, colour): 

        if not album:
            count = len(files) * len(chats) 
        else:
            count = len(chats) 

        for i in range(0, count):
            while True:
                data = sock.recv(4096).decode()
                for line in data.splitlines():
                    msg = json.loads(line)
                    current = msg["current"]
                    total = msg["total"]
                    progress(current, total, colour) 

                if current == total:
                    break

    if path.exists(chat_path) and not args.refresh: 
        await load_chats() 
    else: 
        await reload_chats() 
        print("Refreshed local chat store")
        exit()

    if not args.caption:
        args.caption = [None]

    if not chats:
        chat_list = dict(list(chat_list.items())[:args.nchats])
        chats = await display_list(args.chats, chat_list)  # Display chat list

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(SOCK_PATH)

    # Send Message
    async def send_message(chats, messages):
        for message in messages:
            for chat in chats:
                cmd = {"type": "send_message", "chat": chat[0], "text": message, "reply_to": chat[1]}
                sock.send((json.dumps(cmd) + "\n").encode())

        cmd = {"type": "end"} 
        sock.send((json.dumps(cmd) + "\n").encode())

    # Send Videos
    async def send_videos(chats, videos):
        for video in videos:
            if path.exists(video):
                height, width, duration = meta_extract(video)
                for chat in chats:
                    cmd = {
                        "type": "send_video", "chat": chat[0], 
                        "video": path.abspath(video), "caption": args.caption[0], 
                        "reply_to": chat[1],
                        "height": height, "width": width, "duration": duration,
                        "quiet": args.quiet 
                    }

                    sock.send((json.dumps(cmd) + "\n").encode())
            else:
                print("{} doesnt exist".format(video))
                return 1

        cmd = {"type": "end"} 
        sock.send((json.dumps(cmd) + "\n").encode())

        if not args.quiet:
            display_progress(args.album, videos, chats, args.progress_colour) 

    # Send Images
    async def send_images(chats, images):
        if not args.album:
            for image in images:
                if path.exists(image):
                    for chat in chats:
                        cmd = {
                            "type": "send_image", "chat": chat[0], 
                            "image": path.abspath(image), "caption": args.caption[0], 
                            "reply_to": chat[1], "quiet": args.quiet 
                        }

                        sock.send((json.dumps(cmd) + "\n").encode())
                else:
                    print("{} doesnt exist".format(image))
                    return 1

        else:                                                           # Send images as an album 
            for chat in chats:
                image_paths = [ path.abspath(image) for image in images ]
                cmd = {
                    "type": "send_image", "chat": chat[0], 
                    "image": image_paths, "caption": args.caption[0], 
                    "reply_to": chat[1], "quiet": args.quiet
                }
                sock.send((json.dumps(cmd) + "\n").encode())


        cmd = {"type": "end"} 
        sock.send((json.dumps(cmd) + "\n").encode())

        if not args.quiet:
            display_progress(args.album, images, chats, args.progress_colour) 

    # Send files
    async def send_files(chats, files):
        if not args.album:
            for file in files:
                if path.exists(file):
                    for chat in chats:
                        cmd = {
                            "type": "send_file", "chat": chat[0], 
                            "file": path.abspath(file), "caption": args.caption[0], 
                            "reply_to": chat[1], "quiet": args.quiet
                        }
                        sock.send((json.dumps(cmd) + "\n").encode())
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
                        "type": "send_file", "chat": chat[0], 
                        "file": files_album, "caption": args.caption[0], 
                        "reply_to": chat[1], "quiet": args.quiet
                    }
                    sock.send((json.dumps(cmd) + "\n").encode())

        cmd = {"type": "end"} 
        sock.send((json.dumps(cmd) + "\n").encode())

        if not args.quiet:
            display_progress(args.album, files, chats, args.progress_colour) 

    if args.message:
        await send_message(chats, args.message)
    elif args.image:
        await send_images(chats, args.image)
    elif args.video:
        await send_videos(chats, args.video)
    elif args.file:
        await send_files(chats, args.file)

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

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    if not path.exists(path.join(path.expanduser(CONFIG_DIR) + "dark-send.conf")):
        import dark_send.config as config
        await config.generate_conf()

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
