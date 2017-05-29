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


def download(url, min_file_size = 0, max_file_size = -1,
	         no_redirects = False, pos = 0, mode = 's'):
    global main_it

    file_name = url.split('/')[-1]
    file_address = settings.download_directory + '/' + file_name
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


def initialise_downloads(urls, directory):
    """
    Initialise globals including appJar GUI progress bar.
    Important: Required otherwise lose context when debugging.
    """
    settings.urls_total_count = len(urls)
    settings.urls_processed = 0
    settings.urls_percent_complete = 1
    settings.download_directory = create_new_download_directory(directory)


def open_download_folder():
    """
    Open in a macOS Finder window the directory containing downloaded files
    """
    if sys.platform == "darwin":
        # macOS

        subprocess.Popen(['open', settings.download_directory])

        # TODO - implement for linux and windows
        # elif platform == "linux" or platform == "linux2":
        # elif platform == "win32":


def create_new_download_directory(directory):
    """
    Create new directory name within the root directory's 'downloads' folder.
    Create the root directory's 'downloads' folder if it does not already exist.
    Ensure functionality is correct (i.e. generates 'downloads' directory and new subfolder
    in root project directory and not within an existing subfolder) whether we
    run the executable from the root directory with say `python ctdl/ctdl.py` or
    `python examples/gui.py`, or from within an existing subdirectory where the executable
    is being run from like 'examples' or 'ctdl' such as when run with `cd examples; python gui.py`
    or `cd ctdl; python ctdl.py`.

    :param directory: new directory name to create for files being downloaded
    :return: full path the new directory within the root directory's 'download' folder
    """
    # create directory within root directory's 'downloads' folder to save files
    def get_parent_path():
        test_path = sys.path[0]
        split_on_char = "/"
        return split_on_char.join(test_path.split(split_on_char)[:-1])

    def get_current_directory_name(current_path):
        return current_path.rsplit("/",1)[-1]

    current_path = sys.path[0]
    existing_subfolders = ["ctdl", "examples"]

    if get_current_directory_name(current_path) in existing_subfolders:
        # case when running from within subfolder
        root_project_path = get_parent_path()
    else:
        # case when running from root project directory
        root_project_path = current_path

    main_downloads_path = root_project_path + "/downloads"

    # create main 'downloads' subfolder if not exist
    if not os.path.exists(main_downloads_path):
        os.makedirs(main_downloads_path)

    # create subfolder within 'downloads' folder to save files
    new_download_path = main_downloads_path + "/" + directory
    if not os.path.exists(new_download_path):
        os.makedirs(new_download_path)

    return new_download_path

def download_parallel(urls, directory, min_file_size, max_file_size, no_redirects):
    global main_iter

    initialise_downloads(urls, directory)

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

    initialise_downloads(urls, directory)

    # download files one by one
    for url in urls:
        download(url, min_file_size, max_file_size, no_redirects)

    settings.urls_percent_complete = 100
    print("Download complete.")
    open_download_folder()
