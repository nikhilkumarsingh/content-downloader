import os
import sys
import subprocess
import threading
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm, trange
import settings
import utils

chunk_size = 1024
main_iter = None
yellow_color = "\033[93m"
blue_color = "\033[94m"

# modes -> s: series | p: parallel

s = requests.Session()
# Max retries and back-off strategy so all requests to http:// sleep before retrying
retries = Retry(total = 5,
                backoff_factor = 0.1,
                status_forcelist = [ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries = retries))


def download(url, directory, min_file_size = 0, max_file_size = -1, 
	         no_redirects = False, pos = 0, mode = 's'):
    global main_it

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

    total_chunks = total_size/chunk_size

    if total_chunks < min_file_size: 
    	# ignore this file since file size is lesser than min_file_size
        return
    elif max_file_size != -1 and total_chunks > max_file_size:
    	# ignore this file since file size is greater than max_file_size
        return

    file_iterable = resp.iter_content(chunk_size = chunk_size)

    tqdm_iter = tqdm(iterable = file_iterable, total = total_chunks, 
            unit = 'KB', position = pos, desc = blue_color + file_name, leave = False)

    with open(file_address, 'wb') as f:
        for data in tqdm_iter:
            f.write(data)

    settings.urls_processed += 1
    settings.urls_percent_complete = (settings.urls_processed / settings.urls_total_count) * 100

    if mode == 'p':
        main_iter.update(1)


def open_download_folder():
    """
    Open in a macOS Finder window the directory containing downloaded files
    """
    if sys.platform == "darwin":
        # macOS

        # Cater for when run gui.py file directly in debugger within the examples directory
        download_directory_full = sys.path[0]+'/'+settings.download_directory

        if not os.path.isdir(download_directory_full):
            # Cater for when run gui.py file from project root directory with `python examples/gui.py`
            def get_main_path():
                test_path = sys.path[0] # sys.path[0] is current path in 'examples' subdirectory
                split_on_char = "/"
                return split_on_char.join(test_path.split(split_on_char)[:-1])
            main_path = get_main_path()
            download_directory_full = main_path+"/"+settings.download_directory

        subprocess.Popen(['open', download_directory_full])

        # TODO - implement for linux and windows
        # elif platform == "linux" or platform == "linux2":
        # elif platform == "win32":


def download_parallel(urls, directory, min_file_size, max_file_size, no_redirects):
    global main_iter

    # Initialise globals including appJar GUI progress bar
    # Important: Required otherwise lose context when debugging.
    settings.urls_total_count = len(urls)
    settings.urls_processed = 0
    settings.urls_percent_complete = 1
    settings.download_directory = directory

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

    settings.urls_percent_complete = 100
    print("\n\nDownload complete.")
    open_download_folder()


def download_series(urls, directory, min_file_size, max_file_size, no_redirects):

    # Initialise globals including appJar GUI progress bar.
    # Important: Required otherwise lose context when debugging.
    settings.urls_total_count = len(urls)
    settings.urls_processed = 0
    settings.urls_percent_complete = 1
    settings.download_directory = directory

    # create directory to save files
    if not os.path.exists(directory):
        os.makedirs(directory)

    # download files one by one
    for url in urls:
        download(url, directory, min_file_size, max_file_size, no_redirects)

    settings.urls_percent_complete = 100
    print("Download complete.")
    open_download_folder()
