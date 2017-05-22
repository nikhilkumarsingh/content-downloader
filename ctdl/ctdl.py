import argparse
import requests
from bs4 import BeautifulSoup
from .downloader import download_series, download_parallel
from .utils import FILE_EXTENSIONS

search_url = "https://www.google.com/search"


def scrape(html):
	soup = BeautifulSoup(html, 'html5lib')
	results = soup.findAll('h3', {'class': 'r'})
	links = []
	for result in results:
		link = result.a['href'][7:].split('&')[0]
		links.append(link)
	return links


def search(query, file_type = 'pdf', limit = 10):
	gquery = "filetype:{0} {1}".format(file_type, query)
	params = {
		'q': gquery,
		'start': 0,
	}

	headers = {
		'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) \
		               Gecko/20100101 Firefox/53.0'
	}

	links = []
	
	'''
	every Google search result page has a start index.
	every page contains 10 search results.
	'''
	for start_index in range(0, limit, 10):
		params['start'] = start_index
		resp = requests.get(search_url, params = params, headers = headers)
		page_links = scrape(resp.content)
		links.extend(page_links)

	return links[:limit]


def download_content(query, file_type = 'pdf', directory = None, limit = 10, parallel = False):
	if not directory:
		directory = query.replace(' ', '-')

	print("Downloading {0} {1} files on topic {2} and saving to directory: {3}".
		  format(limit, file_type, query, directory))

	links = search(query, file_type, limit)

	if parallel:
		download_parallel(links, directory)
	else:
		download_series(links, directory)


def show_filetypes():
	for item in FILE_EXTENSIONS.items():
		print("{0:4}: {1}".format(item[1], item[0]))


def main():
    parser = argparse.ArgumentParser(description = "Content Downloader",
    								 epilog="Now download files on any topic in bulk!")
 
    # defining arguments for parser object
    parser.add_argument("query", type = str, default = None, nargs = '?',
    					help = "Specify the query.")

    parser.add_argument("-f", "--file_type", type = str, default = 'pdf',
                        help = "Specify the extension of files to download.")
     
    parser.add_argument("-l", "--limit", type = int, default = 10,
                        help = "Limit the number of search results (in multiples of 10).")
     
    parser.add_argument("-d", "--directory", type = str, default = None,
                        help = "Specify directory where files will be stored.")

    parser.add_argument("-p", "--parallel", action = 'store_true',
                        help = "For parallel downloading.")

    parser.add_argument("-a", "--available", action='store_true',
    					help = "Get list of all available filetypes.")
 
    args = parser.parse_args()
  
    if args.available:
    	show_filetypes()
    else:
    	download_content(args.query, args.file_type, args.directory, args.limit, args.parallel)


if __name__ == "__main__":
	main()
