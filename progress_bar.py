from time import sleep 
from threading import Thread
from rich.progress import Progress

flag,no_iter,prev_count = False, 0, 0
num_arr = []
no_thread = 0

def percentage(part,whole): 
    per_num = 100 * float(part)/float(whole)
    return round(per_num,0)

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
              prev_count = bar_count
              for i in range(int(prev_count)):
                  while True:
                      if flag == False:
                          flag = True
                          break

              num_arr.append(bar_count)
              if bar_count == 100:
                  for i in range(int(prev_count),100): 
                      while True:
                          flag = True

                  prev_count,no_thread = 0, 0 
                  num_arr = []
                  return
          else:
              for i in range(int(bar_count - prev_count)):
                  while True:
                      if flag == False: 
                          flag = True
                          break

              prev_count = bar_count
              num_arr.append(bar_count)

              if bar_count == 100:
                  for i in range(int(prev_count),100): 
                      while True:
                          flag = True

                  prev_count = 0 
                  return


def bar_func(): 
   
    global no_iter
    global flag

#    with alive_bar(100,title='Uploading') as bar: 
#        while True: 
#            if no_iter == 100: 
#                no_iter = 0 
#                break 
#
#            if flag == True: 
#                bar() 
#                no_iter += 1
#                flag = False 

    with Progress() as bar: 
        upload_task = bar.add_task("[green]Uploading...",total=100) 

        while True: 
            if no_iter == 100: 
                no_iter = 0
                break

            if flag == True: 
                bar.advance(upload_task)
                no_iter += 1
                flag = False

