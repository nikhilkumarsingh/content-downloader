import sys
import argparse
import requests
import urllib
try:
	from urllib.request import urlopen
	from urllib.error import HTTPError
except ImportError:
	from urllib2 import urlopen
	from urllib2 import HTTPError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from downloader import download_series, download_parallel
from utils import FILE_EXTENSIONS, THREAT_EXTENSIONS, DEFAULTS


s = requests.Session()
# Max retries and back-off strategy so all requests to http:// sleep before retrying
retries = Retry(total=5,
				backoff_factor=0.1,
				status_forcelist=[ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))

	
def get_google_links(limit, params, headers):
	"""
	function to fetch links equal to limit

	every Google search result page has a start index.
	every page contains 10 search results.
	"""
	links = []
	for start_index in range(0, limit, 10):
		params['start'] = start_index
		resp = s.get("https://www.google.com/search", params = params, headers = headers)
		page_links = scrape_links(resp.content, engine = 'g')
		links.extend(page_links)
	return links[:limit]



def get_duckduckgo_links(limit, params, headers):
	"""
	function to fetch links equal to limit

	duckduckgo pagination is not static, so there is a limit on
	maximum number of links that can be scraped
	"""
	resp = s.get('https://duckduckgo.com/html', params = params, headers = headers)
	links = scrape_links(resp.content, engine = 'd')
	return links[:limit]


def scrape_links(html, engine):
	"""
	function to scrape file links from html response
	"""
	soup = BeautifulSoup(html, 'lxml')
	links = []

	if engine == 'd':
		results = soup.findAll('a', {'class': 'result__a'})
		for result in results:
			link = result.get('href')[15:]
			link = link.replace('/blob/', '/raw/')
			links.append(link)

	elif engine == 'g':
		results = soup.findAll('h3', {'class': 'r'})   	
		for result in results:
			link = result.a['href'][7:].split('&')[0]
			link = link.replace('/blob/', '/raw/')
			links.append(link)

	return links




def get_url_nofollow(url):
	""" 
	function to get return code of a url

	Credits: http://blog.jasonantman.com/2013/06/python-script-to-check-a-list-of-urls-for-return-code-and-final-return-code-if-redirected/
	"""
	try:
		response = urlopen(url)
		code = response.getcode()
		return code
	except HTTPError as e:
		return e.code
	except:
		return 0


def validate_links(links):
	"""
	function to validate urls based on http(s) prefix and return code
	"""
	valid_links = []
	for link in links:
		if link[:7] in "http://" or link[:8] in "https://":
			valid_links.append(link)
	
	if not valid_links:
		print("No files found.")
		sys.exit(0)

	# checking valid urls for return code
	urls = {}
	for link in valid_links:
		if 'github.com' and '/blob/' in link:
			link = link.replace('/blob/', '/raw/')
		urls[link] = {'code': get_url_nofollow(link)}
		
	
	# printing valid urls with return code 200
	available_urls = []
	for url in urls:
		print("code: %d\turl: %s" % (urls[url]['code'], url))
		if urls[url]['code'] != 0:
			available_urls.append(url)

	return available_urls


def search(query, engine='g', site="", file_type = 'pdf', limit = 10):
	"""
	main function to search for links and return valid ones
	"""
	if site == "":
		search_query = "filetype:{0} {1}".format(file_type, query)
	else:
		search_query = "site:{0} filetype:{1} {2}".format(site,file_type, query)

	headers = {
		'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) \
		Gecko/20100101 Firefox/53.0'
	}
	if engine == "g":
		params = {
			'q': search_query,
			'start': 0,
		}
		links = get_google_links(limit, params, headers)

	elif engine == "d":
		params = {
			'q': search_query,
		}
		links = get_duckduckgo_links(limit,params,headers)
	else:
		print("Wrong search engine selected!")
		sys.exit()
	
	valid_links = validate_links(links)
	return valid_links


def check_threats(**args):
	"""
	function to check input filetype against threat extensions list 
	"""
	is_high_threat = False
	for val in THREAT_EXTENSIONS.values():
		if type(val) == list:
			for el in val:
				if args['file_type'] == el:
					is_high_threat = True
					break
		else:
			if args['file_type'] == val:
				is_high_threat = True
				break
	return is_high_threat


def validate_args(**args):
	"""
	function to check if input query is not None 
	and set missing arguments to default value
	"""
	if not args['query']:
		print("\nMissing required query argument.")
		sys.exit()

	for key in DEFAULTS:
		if key not in args:
			args[key] = DEFAULTS[key]

	return args


def download_content(**args):
	"""
	main function to fetch links and download them
	"""
	args = validate_args(**args)

	if not args['directory']:
		args['directory'] = args['query'].replace(' ', '-')

	print("Downloading {0} {1} files on topic {2} from {3} and saving to directory: {4}"
		.format(args['limit'], args['file_type'], args['query'], args['website'], args['directory']))
		

	links = search(args['query'], args['engine'], args['website'], args['file_type'], args['limit'])

	if args['parallel']:
		download_parallel(links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])
	else:
		download_series(links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])


def show_filetypes(extensions):
	"""
	function to show valid file extensions
	"""
	for item in extensions.items():
		val = item[1]
		if type(item[1]) == list:
			val = ", ".join(str(x) for x in item[1])
		print("{0:4}: {1}".format(val, item[0]))


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

	parser.add_argument("-p", "--parallel", action = 'store_true', default = False,
						help = "For parallel downloading.")

	parser.add_argument("-e", "--engine", type=str, default = "g",
						help = "Specify search engine\nduckduckgo: 'd'\ngoogle: 'g'")

	parser.add_argument("-a", "--available", action='store_true',
						help = "Get list of all available filetypes.")

	parser.add_argument("-w", "--website", type = str,  default = "",
						help = "specify website.")

	parser.add_argument("-t", "--threats", action='store_true',
						help = "Get list of all common virus carrier filetypes.")

	parser.add_argument("-minfs", "--min-file-size", type = int, default = 0,
						help = "Specify minimum file size to download in Kilobytes (KB).")

	parser.add_argument("-maxfs", "--max-file-size", type = int, default = -1,
						help = "Specify maximum file size to download in Kilobytes (KB).")

	parser.add_argument("-nr", "--no-redirects", action = 'store_true', default = False,
						help = "Prevent download redirects.")

	parser.add_argument("-w", "--website", default = None, type = str,
						help = "Specify a particular website to download content from.")

	args = parser.parse_args()
	args_dict = vars(args)

	if args.available:
		show_filetypes(FILE_EXTENSIONS)
		return

	if args.threats:
		show_filetypes(THREAT_EXTENSIONS)
		return

	high_threat = check_threats(**args_dict)

	if high_threat:
		def prompt(message, errormessage, isvalid, isexit):
			res = None
			while res is None:
				res = input(str(message)+': ')
				if isexit(res):
					sys.exit()
				if not isvalid(res):
					print(str(errormessage))
					res = None
			return res
		prompt(
			message = "WARNING: Downloading this file type may expose you to a heightened security risk.\nPress 'y' to proceed or 'n' to exit",
			errormessage= "Error: Invalid option provided.",
			isvalid = lambda x:True if x is 'y' else None,
			isexit = lambda x:True if x is 'n' else None
		)

	download_content(**args_dict)


if __name__ == "__main__":
	main()
