import os
import threading
import requests
from multiprocessing import Queue
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm, trange
from tkinter import ttk

from tkinter import *

chunk_size = 1024
total_chunks =-1
main_iter = None
yellow_color = "\033[93m"
blue_color = "\033[94m"

# modes -> s: series | p: parallel
queueLock = threading.Lock()
queueLock2 = threading.Lock()

i_max=0

s = requests.Session()
# Max retries and back-off strategy so all requests to http:// sleep before retrying
retries = Retry(total = 5,
                backoff_factor = 0.1,
                status_forcelist = [ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries = retries))


def download(url, directory,min_file_size = 0, max_file_size = -1, 
             no_redirects = False, pos = 0, mode = 's'):
    global main_it
    global total_chunks

    file_name = url.split('/')[-1]
    file_address = directory + '/' + file_name
    is_redirects = not no_redirects

    resp = s.get(url, stream = True, allow_redirects = is_redirects)

    if not resp.status_code == 200:
        # ignore this file since server returns invalid response
        return

    try:
        total_size = int(resp.headers['content-length'])
    except KeyError:
        total_size = len(resp.content)

    queueLock.acquire()

    total_chunks = total_size/chunk_size
    print(total_size)
    queueLock.release()


    if total_chunks < min_file_size: 
        # ignore this file since file size is lesser than min_file_size
        return
    elif max_file_size != -1 and total_chunks > max_file_size:
        # ignore this file since file size is greater than max_file_size
        return

    file_iterable = resp.iter_content(chunk_size = chunk_size)

    tqdm_iter = tqdm(iterable = file_iterable, total = total_chunks, 
            unit = 'KB', position = pos, desc =  file_name, leave = False)
    global i_max

    with open(file_address, 'wb') as f:
        i=0
        for data in tqdm_iter:
            i=i+1
            i_max=i
            f.write(data)

    if mode == 'p':
        main_iter.update(1)



class myThread (threading.Thread):
    def __init__(self,url,directory,min_file_size,max_file_size,no_redirects ):
        threading.Thread.__init__(self)
        self.url = url
        self.directory = directory
        self.min_file_size=min_file_size
        self.max_file_size=max_file_size
        self.no_redirects=no_redirects

    def run(self):
        print ("Starting")
        download(self.url, self.directory ,self.min_file_size, self.max_file_size, self.no_redirects )
        print ("Exiting" )




class progress_class(Tk):

    def __init__(self,url,directory , min_file_size,max_file_size,no_redirects):
        Tk.__init__(self)
        self.url = url
        self.directory = directory
        self.min_file_size=min_file_size
        self.max_file_size=max_file_size
        self.no_redirects=no_redirects

        self.button = Button(self,text="start", command=self.start)
        self.button.pack(fill=X)
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        length=300, mode="determinate")
        self.progress.pack()
        self.bytes = 0
        self.maxbytes = 0

    def start(self):

        self.thread = myThread(self.url,self.directory , self.min_file_size, self.max_file_size, self.no_redirects )
        self.progress["value"] = 0
        self.bytes=0
        self.thread.start()

        while True:
            queueLock.acquire()
            if total_chunks==-1:
                queueLock.release()
            else :
                self.maxbytes=total_chunks
                self.progress["maximum"]=total_chunks
                queueLock.release()
                break

        self.read_bytes()

        print( "in progress start")
        # self.thread.join()
        print( " in progress ends")


    def read_bytes(self):
        '''simulate reading 500 bytes; update progress bar'''
        global i_max
        self.bytes =i_max

        self.progress["value"] = self.bytes
        if self.bytes < self.maxbytes:
            # read more bytes after 1 ms
            self.after(1, self.read_bytes)



def download_parallel_gui(urls, directory, min_file_size, max_file_size, no_redirects):
    global main_iter

    # create directory to save files
    if not os.path.exists(directory):
        os.makedirs(directory)

    # overall progress bar
    main_iter = trange(len(urls), position = 1, desc = yellow_color + "Overall")

    # empty list to store threads
    threads = []

    # creating threads
    for idx, url in enumerate(urls):
        t = threading.Thread(
            target = download,
            kwargs = {
                'url': url,
                'directory': directory,
                'pos': 2*idx+3,
                'mode': 'p',
                'min_file_size': min_file_size,
                'max_file_size': max_file_size,
                'no_redirects': no_redirects
            }
        )
        threads.append(t)

    # start all threads
    for t in threads:
        t.start()

    # wait until all threads terminate
    for t in threads[::-1]:
        t.join()

    main_iter.close()

    print("\n\nDownload complete.")


def download_series_gui(urls, directory, min_file_size, max_file_size, no_redirects):

    # create directory to save files
    if not os.path.exists(directory):
        os.makedirs(directory)




    app=progress_class(urls[0],directory, min_file_size,max_file_size,no_redirects)

    
    app.mainloop()

    # app=SampleApp()
    # app.mainloop()

    print("Download complete.")

