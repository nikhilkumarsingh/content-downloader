import sys
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


def validate_args(**args):
    if not args['query']:
        print("\nMissing required query argument.")
        sys.exit()


def download_content(**args):
    if not args['directory']:
        args['directory'] = args['query'].replace(' ', '-')

    print("Downloading {0} {1} files on topic {2} and saving to directory: {3}"
        .format(args['limit'], args['file_type'], args['query'], args['directory']))

    links = search(args['query'], args['file_type'], args['limit'])

    if args['parallel']:
        download_parallel(links, args['directory'])
    else:
        download_series(links, args['directory'])


def show_filetypes(extensions):
	for item in extensions.items():
		print("{0:4}: {1}".format(item[1], item[0]))


def main():
    parser = argparse.ArgumentParser(description = "Content Downloader",
    								 epilog="Now download files on any topic in bulk!")
 
    # defining arguments for parser object
    parser.add_argument("query", type = str, default = None, nargs = '?',
    					help = "Specify the query.")

    parser.add_argument("-g", "--file_type", type = str, default = 'pdf',
                        help = "Specify the extension of files to download.")
     
    parser.add_argument("-l", "--limit", type = int, default = 10,
                        help = "Limit the number of search results (in multiples of 10).")
     
    parser.add_argument("-d", "--directory", type = str, default = None,
                        help = "Specify directory where files will be stored.")

    parser.add_argument("-p", "--parallel", action = 'store_true', default = False,
                        help = "For parallel downloading.")

    parser.add_argument("-a", "--available", action='store_true',
    					help = "Get list of all available filetypes.")

    parser.add_argument("-t", "--threats", action='store_true',
                        help = "Get list of all common virus carrier filetypes.")
 
    args = parser.parse_args()
    args_dict = vars(args)

    if args.available:
        show_filetypes(FILE_EXTENSIONS)
        return

    validate_args(**args_dict)

    download_content(**args_dict)


if __name__ == "__main__":
	main()
