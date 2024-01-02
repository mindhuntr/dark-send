from rich.progress import Progress, SpinnerColumn 
from threading import Thread

flag,prev_count,no_thread,album_count = False, 0, 0, None
num_arr = []

def percentage(part,whole): 

    global album_count 
    if not album_count: 
        album_count = whole

    per_num = 100 * int(part)/int(album_count)
    
    return int(per_num) 

def progress(current,total):
      # print('Uploaded', current, 'out of', total,
      #      'bytes: {:.2%}'.format(current / total))

      global num_arr
      global flag
      global prev_count
      global no_thread
      global album_count 

      if no_thread == 0: 
          bar_thread = Thread(target=bar_func) 
          bar_thread.start() 
          no_thread = 1
      
      bar_count = percentage(current,total)

      if not bar_count in num_arr: 
          if not num_arr: 
              if bar_count >= 100 and prev_count == 0: 
                  for _ in range(0,100): 
                      while True: 
                          if flag == False: 
                              flag = True
                              break
                  no_thread = 0
                  album_count = None

              elif bar_count != 100: 

                   prev_count = bar_count
                   num_arr.append(bar_count) 

                   for _ in range(prev_count): 
                       while True: 
                           if flag == False: 
                               flag = True
                               break 

          else:
              if bar_count >= 100:
                  for _ in range(prev_count,100): 
                      while True:
                          if flag == False: 
                              flag = True
                              break 

                  no_thread,prev_count,album_count = 0, 0, None
                  num_arr = [] 

              else: 
                  for _ in range(bar_count - prev_count): 
                      while True: 
                          if flag == False: 
                              flag = True
                              break

                  prev_count = bar_count 
                  num_arr.append(bar_count) 


def bar_func(): 
   
    global flag
    global no_thread

    with Progress(SpinnerColumn(),*Progress.get_default_columns()) as bar: 
        upload_task = bar.add_task("[green]Up/Down...",total=100) 

        for _ in range(0,100): 
            while True: 
                if flag == True: 
                    bar.advance(upload_task)
                    flag = False
                    break

