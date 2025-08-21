from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

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

