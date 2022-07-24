from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


def meta_extract(filename): 

    parser = createParser(filename) 

    if not parser: 
        print("Unable to parse file") 
        return 1 

    try: 
        metadata = extractMetadata(parser) 

        duration = metadata.get('duration').seconds
        width = metadata.get('width')
        height = metadata.get('height') 

        return height,width,duration 
    
    except: 
        print("Unable to extract metadata") 
        return 1 

