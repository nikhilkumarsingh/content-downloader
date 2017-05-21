[![PyPI](https://img.shields.io/badge/PyPi-v1.2-f39f37.svg)](https://pypi.python.org/pypi/ctdl)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/nikhilkumarsingh/content-downloader/blob/master/LICENSE.txt)

# content-downloader

Python package to download files on any topic in bulk.

content-downloader supports Python 2 as well as Python 3.

## Installation

To install content-downloader, simply,
```
$ pip install ctdl
```

## Command line usage

```
$ ctdl [-h] [-f FILE_TYPE] [-l LIMIT] [-d DIRECTORY] [-a] [query]
```
Optional arguments are:

- -f FILE_TYPE : set the file type. (can take values like ppt, pdf, xml, etc.)

                 Default value: pdf

- -l LIMIT : specify the number of files to download.

             Default value: 10

- -d DIRECTORY : specify the directory where files will be stored.

                 Default: A directory with same name as the search query in the current directory.

Here are some examples:

- To get list of available filetypes:

  ```
  $ ctdl -a
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

- To expicitly specify download folder:

  ```
  $ ctdl -d /home/nikhil/Desktop/ml-pdfs machine learning
  ```


## Usage in Python files

```python
from ctdl import ctdl

filetype = 'ppt'
limit = 5
directory = '/home/nikhil/Desktop/ml-pdfs'
query = 'machine learning using python'

ctdl.download_content(query, filetype, directory, limit)
```

![](https://github.com/nikhilkumarsingh/content-downloader/blob/master/example.png)
