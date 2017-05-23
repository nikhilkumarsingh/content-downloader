import os
import threading
import requests
from tqdm import tqdm, trange

chunk_size = 1024
main_iter = None
yellow_color = "\033[93m"
blue_color = "\033[94m"

# modes -> s: series | p: parallel

def download(url, directory, pos = 0, mode = 's'):
    global main_it

    file_name = url.split('/')[-1]
    file_address = directory + '/' + file_name

    resp = requests.get(url, stream = True)
    try:
        total_size = int(resp.headers['content-length'])
    except KeyError:
        total_size = len(resp.content)

    total_chunks = total_size/chunk_size
    file_iterable = resp.iter_content(chunk_size = chunk_size)

    tqdm_iter = tqdm(iterable = file_iterable, total = total_chunks, 
            unit = 'KB', position = pos, desc = blue_color + file_name, leave = False)

    with open(file_address, 'wb') as f:
        for data in tqdm_iter:
            f.write(data)

    if mode == 'p':
        main_iter.update(1)


def download_parallel(urls, directory):
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
        t = threading.Thread(target = download, kwargs = {'url': url, 
            'directory': directory, 'pos': 2*idx+3, 'mode': 'p'})
        threads.append(t)

    # start all threads
    for t in threads:
        t.start()

    # wait until all threads terminate
    for t in threads[::-1]:
        t.join()

    print("\nDownload complete.")


def download_series(urls, directory):

    # create directory to save files
    if not os.path.exists(directory):
        os.makedirs(directory)

    # download files one by one
    for url in urls:
        download(url, directory)

    print("Download complete.")