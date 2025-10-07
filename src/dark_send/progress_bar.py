from tqdm import tqdm 
import time


progress_bar = None 
start_time = time.time()


def convert_bytes(size):
    for x in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {x}"
        size /= 1024.0
    return size

def progress(downloaded, fileSize, colour):

    global start_time
    global progress_bar 

    second = time.time() - start_time
    speed = int((downloaded / second) / 1000)
    percent = int((downloaded/fileSize)*100)
    bars = int(percent/5)

    if progress_bar is None: 
        progress_bar = tqdm(range(100), bar_format='{l_bar}{bar:40}{r_bar}{bar:-40b}',colour=colour, ascii="⣀⣄⣤⣦⣶⣷⣿") 

    progress_bar.n = percent
    progress_bar.refresh()

    if progress_bar.n >= 100:
        progress_bar.close()
        progress_bar = None 

