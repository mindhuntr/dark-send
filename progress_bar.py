from time import sleep 
from threading import Thread
from rich.progress import Progress

flag,prev_count = False, 0, 
num_arr = []
no_thread = 0

def percentage(part,whole): 
    per_num = 100 * float(part)/float(whole)
    return int(per_num) 

def progress(current,total):
      # print('Uploaded', current, 'out of', total,
      #      'bytes: {:.2%}'.format(current / total))

      global num_arr
      global flag
      global prev_count
      global no_thread

      if no_thread == 0: 
          bar_thread = Thread(target=bar_func) 
          bar_thread.start() 
          no_thread = 1
      
      bar_count = percentage(current,total)

      if not bar_count in num_arr: 
          if not num_arr: 
              if bar_count == 100 and prev_count == 0: 
                  for i in range(0,100): 
                      while True: 
                          if flag == False: 
                              flag = True
                              break
                  no_thread = 0

              elif bar_count != 100: 

                   prev_count = bar_count
                   num_arr.append(bar_count) 

                   for i in range(prev_count): 
                       while True: 
                           if flag == False: 
                               flag = True
                               break 

          else:
              if bar_count == 100:
                  for i in range(prev_count,100): 
                      while True:
                          if flag == False: 
                              flag = True
                              break 

                  no_thread,prev_count = 0, 0
                  num_arr = [] 

              else: 
                  for i in range(bar_count - prev_count): 
                      while True: 
                          if flag == False: 
                              flag = True
                              break

                  prev_count = bar_count 
                  num_arr.append(bar_count) 


def bar_func(): 
   
    global flag
    global no_thread

    with Progress() as bar: 
        upload_task = bar.add_task("[green]Uploading...",total=100) 

        for i in range(0,100): 
            while True: 
                if flag == True: 
                    bar.advance(upload_task)
                    flag = False
                    break

