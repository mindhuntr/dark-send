from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from moviepy.editor import VideoFileClip
from PIL import Image
import io

def meta_extract(filename): 

    parser = createParser(filename) 

    if not parser: 
        print("Unable to parse file") 
        return 1 

    try:
        metadata = extractMetadata(parser) 
        meta_dict = vars(metadata) 

        if '_MultipleMetadata__key_counter' not in meta_dict: 
            duration = metadata.get('duration').seconds
            width = metadata.get('width') 
            height = metadata.get('height')
        else:
            duration = metadata.get('duration').seconds
            width = meta_dict['_MultipleMetadata__groups']['video[1]'].get('width')
            height = meta_dict['_MultipleMetadata__groups']['video[1]'].get('height')
        
        return height, width, duration 

    except: 

        print("Unable to extract metadata") 
        return 1, 1, 1

def extract_thumb(thumbnail, video_path, time=1, size=(320, 320)): 

    if thumbnail: 
        with Image.open(thumbnail) as img: 

            img_resized = img.resize(size)
            img_byte_arr = io.BytesIO()

            img_resized.save(img_byte_arr, format='JPEG')

            img_byte_arr.seek(0)  # Go to the start of the BytesIO object
            img_bytes = img_byte_arr.read()
            
            return img_bytes

    clip = VideoFileClip(video_path)
    frame = clip.get_frame(time)
    frame_image = Image.fromarray(frame)

    frame_image = frame_image.resize(size)
    
    byte_io = io.BytesIO()
    frame_image.save(byte_io, format='JPEG')
    byte_io.seek(0)

    return byte_io

