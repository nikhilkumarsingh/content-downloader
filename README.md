[![PyPI](https://img.shields.io/badge/PyPi-v1.4-f39f37.svg)](https://pypi.python.org/pypi/ctdl)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/nikhilkumarsingh/content-downloader/blob/master/LICENSE.txt)

# content-downloader

Python package with **command line utility** to download files on any topic in bulk.

![](https://media.giphy.com/media/3oKIPlt7APHqWuVl3q/giphy.gif)

## Features

- ctdl fetches file links related to a search query from **Google Search**.

- Files can be downloaded parallely using multithreading.

- ctdl is Python 2 as well as Python 3 compatible.

## Installation

- To install content-downloader, simply,

  ```
  $ pip install ctdl
  $ pip install -U .
  ```

## Important Notes

- If you get error `ModuleNotFoundError: No module named ___` then
run all commands with `python ctdl/ctdl.py ___` instead of `ctdl ___`

- There seem to be some issues with parallel progress bars in tqdm which have
  been resolved in this [pull](https://github.com/tqdm/tqdm/pull/385). Until this pull is merged, please use my patch by running this command:

  ```
  $ pip install -U git+https://github.com/nikhilkumarsingh/tqdm
  ```

## Command line usage

```
$ ctdl [-h] [-f FILE_TYPE] [-l LIMIT] [-d DIRECTORY] [-p] [-a] [-t]
       [-minfs MIN_FILE_SIZE] [-maxfs MAX_FILE_SIZE] [-nr]
       [query]
```

Optional arguments are:

- -f FILE_TYPE : set the file type. (can take values like ppt, pdf, xml, etc.)

                 Default value: pdf

- -l LIMIT : specify the number of files to download.

             Default value: 10

- -d DIRECTORY : specify the directory where files will be stored.

                 Default: A directory with same name as the search query in the current directory.

- -p : for parallel downloading.

- -a : list of all available filetypes.

- -t : list of all common virus carrier filetypes.

- -minfs MIN_FILE_SIZE : specify minimum file size to download in Kilobytes (KB).

                 Default: 0

- -maxfs MAX_FILE_SIZE : specify maximum file size to download in Kilobytes (KB).

                 Default: -1 (represents no maximum file size)

- -nr : prevent download redirects.

                 Default: False


## Examples

- To get list of available filetypes:

  ```
  $ ctdl -a
  ```

- To get list of potential high threat filetypes:

  ```
  $ ctdl -t
  ```

- To download pdf files on topic 'python':

  ```
  $ ctdl python
  ```
  This is the default behaviour which will download 10 pdf files in a folder named 'python' in current directory.

- To download 3 ppt files on 'health':

  ```
  $ ctdl -f ppt -l 3 health
  ```

- To explicitly specify download folder:

  ```
  $ ctdl -d /home/nikhil/Desktop/ml-pdfs machine-learning
  ```

- To download files parallely:
  ```
  $ ctdl -f pdf -p python
  ```

- To search for and download in parallel 10 files in PDF format containing
  the text "python" and "algorithm", without allowing any url redirects,
  and where the file size is between 10,000 KB (10 MB) and 100,000KB (100 MB),
  where KB means Kilobytes, which has an equivalent value expressed in Megabytes:
  ```
  $ ctdl -f pdf -l 10 -minfs 10000 -maxfs 100000 -nr -p "python algorithm"
  ```

### GUI - using appJar

* Install appJar. See [appJar Widgets for info](http://appjar.info/pythonWidgets/)

    ```
    pip install appjar pyyaml
    ```

* Start GUI

    ```
    python examples/gui.py
    ```

    ![alt tag](https://raw.githubusercontent.com/ltfschoen/content-downloader/master/screenshots/gui_appjar_updated.png)

* Automatically opens in a Finder window the directory containing the downloaded files when download completes

## Flask server API with Query Parameters usage

* Install Flask dependency:

    ```
    pip install flask
    ```

* Start a Flask server in a Terminal Window No. 1:

    ```
    python examples/server.py
    ```

    ![alt tag](https://raw.githubusercontent.com/ltfschoen/content-downloader/master/screenshots/flask_server_running.png)

* Open another Terminal Window No. 2 and run cURL passing Query Parameters:

    * Example 1:
        * Note: Defaults are applied for any missing parameters, as shown in logs of screenshot below.
        The `query` values are mandatory.
        ```
        curl -i "http://localhost:5000/api/v1.0/query?query=dogs,cats"
        ```

    * Example 2:
        * Note: Explicitely override Defaults that would be otherwise applied
        ```
        curl -i "http://localhost:5000/api/v1.0/query?query=dogs,cats&file_type=pdf&limit=5&directory=None&parallel=True&available=False&threats=False&min_file_size=0&max_file_size=-1&no_redirects=True"
        ```

    ![alt tag](https://raw.githubusercontent.com/ltfschoen/content-downloader/master/screenshots/curl_query_to_flask_server.png)

* Go back to Terminal Window No. 1 to see the Flask server process your downloads and
and saves them in new folder 'dogs-cats' (which is named based on the query parameters)

    ![alt tag](https://raw.githubusercontent.com/ltfschoen/content-downloader/master/screenshots/flask_server_running_and_processes_curl_request.png)

## Usage in Python files

```python
from ctdl import ctdl

filetype = 'ppt'
limit = 5
directory = '/home/nikhil/Desktop/ml-pdfs'
query = 'machine learning using python'

ctdl.download_content(query, filetype, directory, limit)
```

## TODO

- [X] Prompt user before downloading potentially threatful files
- [X] Example Flask server API implementation with query parameters
- [ ] Implement unit testing
- [X] Create ctdl GUI (using appJar)
- [ ] Use DuckDuckgo API as an option
- [X] macOS - Automatically open directory where files were downloaded when download completes
- [ ] Windows - Automatically open directory where files were downloaded when download completes
- [ ] Linux - Automatically open directory where files were downloaded when download completes

## Want to contribute?

- Clone the repository

  ```
  $ git clone http://github.com/nikhilkumarsingh/content-downloader
  ```

- Install dependencies
  ```
  $ pip install -r requirements.txt
  ```

**Note:** There seem to be some issues with current version of tqdm. If you do not get
expected progress bar behaviour, try this patch:

  ```
  $ pip uninstall tqdm
  $ pip install git+https://github.com/nikhilkumarsingh/tqdm
  ```

* If you have any other issues running `ctdl` and loading modules then run the following
(since `ctdl` command calls the PyPI ctdl package):

    ```
    $ pip install -U .
    ```

    * If the problem still persists then in ctdl/ctdl.py, try removing the `.` prefix
    from `.downloader` and `.utils` for the following imports, so it changes from:
        ```python
        from .downloader import download_series, download_parallel
        from .utils import FILE_EXTENSIONS, THREAT_EXTENSIONS
        ```
        to:
        ```python
        from downloader import download_series, download_parallel
        from utils import FILE_EXTENSIONS, THREAT_EXTENSIONS
        ```

    * Also try running the python file directly with `python ctdl/ctdl.py ___`
    (instead of with `ctdl ___`)
