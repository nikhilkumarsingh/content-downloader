import sys
import argparse
import requests
import urllib
import yaml
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
try:
    from urllib.error import HTTPError
except:
    from urllib2 import HTTPError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
from downloader import download_series, download_parallel
from utils import DEFAULT_ARGS, FILE_EXTENSIONS, THREAT_EXTENSIONS

search_url = "https://www.google.com/search"

s = requests.Session()
# Max retries and back-off strategy so all requests to http:// sleep before retrying
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])
s.mount('http://', HTTPAdapter(max_retries=retries))


def scrape(html):
    """
    function to scrape file links from html response
    """
    soup = BeautifulSoup(html, 'lxml')
    results = soup.findAll('h3', {'class': 'r'})
    links = []
    for result in results:
        link = result.a['href'][7:].split('&')[0]
        links.append(link)
    return links


def get_links(limit, params, headers):
    """
    function to fetch links equal to limit

    every Google search result page has a start index.
    every page contains 10 search results.
    """
    links = []
    for start_index in range(0, limit, 10):
        params['start'] = start_index
        resp = s.get(search_url, params = params, headers = headers)
        page_links = scrape(resp.content)
        links.extend(page_links)
    return links[:limit]


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

    # checking valid urls for return code
    urls = {}
    for link in valid_links:
        urls[link] = {'code': get_url_nofollow(link)}

    # printing valid urls with return code 200
    available_urls = []
    for url in urls:
        print("code: %d\turl: %s" % (urls[url]['code'], url))
        if urls[url]['code'] != 0:
            available_urls.append(url)

    return available_urls


def search(query, file_type = 'pdf', limit = 10):
    """
    main function to search for links and return valid ones
    """
    gquery = "filetype:{0} {1}".format(file_type, query)
    params = {
        'q': gquery,
        'start': 0,
    }
    headers = {
        'User Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:53.0) \
        Gecko/20100101 Firefox/53.0'
    }
    links = get_links(limit, params, headers)
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
    """
    if not args['query']:
        print("\nMissing required query argument.")
        sys.exit()


def download_content(**args):
    """
    main function to fetch links and download them
    """
    args['query'] = args['query'].replace(',', ' ')
    if not args['directory']:
        args['directory'] = args['query'].replace(' ', '-')

    print("Downloading {0} {1} files on topic {2} and saving to directory: {3}"
        .format(args['limit'], args['file_type'], args['query'], args['directory']))

    links = search(args['query'], args['file_type'], args['limit'])

    if args['parallel']:
        download_parallel(links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])
    else:
        download_series(links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])


def show_filetypes(extensions):
    """
    function to show valid file extensions
    """
    print(yaml.dump(extensions, default_flow_style=False))


def main(query_params={}, **args):

    parser = argparse.ArgumentParser(description = "Content Downloader",
    								 epilog="Now download files on any topic in bulk!")

    # defining arguments for parser object
    parser.add_argument("query", type = str, default = DEFAULT_ARGS['query'], nargs = '?',
    					help = "Specify the query.")

    parser.add_argument("-f", "--file_type", type = str, default = DEFAULT_ARGS['file_type'],
                        help = "Specify the extension of files to download.")

    parser.add_argument("-l", "--limit", type = int, default = DEFAULT_ARGS['limit'],
                        help = "Limit the number of search results (in multiples of 10).")

    parser.add_argument("-d", "--directory", type = str, default = DEFAULT_ARGS['directory'],
                        help = "Specify directory where files will be stored.")

    parser.add_argument("-p", "--parallel", action = 'store_true', default = DEFAULT_ARGS['parallel'],
                        help = "For parallel downloading.")

    parser.add_argument("-a", "--available", action='store_true',
    					help = "Get list of all available filetypes.")

    parser.add_argument("-t", "--threats", action='store_true',
                        help = "Get list of all common virus carrier filetypes.")

    parser.add_argument("-minfs", "--min-file-size", type = int, default = DEFAULT_ARGS['min_file_size'],
                        help = "Specify minimum file size to download in Kilobytes (KB).")

    parser.add_argument("-maxfs", "--max-file-size", type = int, default = DEFAULT_ARGS['max_file_size'],
                        help = "Specify maximum file size to download in Kilobytes (KB).")

    parser.add_argument("-nr", "--no-redirects", action = 'store_true', default = DEFAULT_ARGS['no_redirects'],
                        help = "Prevent download redirects.")

    args = parser.parse_args()
    args_dict = vars(args)

    print("CTDL received Flask API endpoint Query Parameters: ", query_params, file=sys.stderr)
    print("CTDL using CLI Arguments: ", args_dict, file=sys.stderr)

    mapped_query_params = {}
    if len(query_params):
        def add_missing_keys_with_defaults(query_params):
            """
            Add defaults where not provided in Query Parameters
            """
            for key, val in DEFAULT_ARGS.items():
                if not key in query_params:
                    query_params[key] = val
            return query_params

        def map_query_params(query_params):
            """
            Convert Query Parameter values to correct type
            """
            mapped_query_params = {}
            for key, val in query_params.items():
                if val == 'None':
                    mapped_query_params[key] = None
                elif val == 'True':
                    mapped_query_params[key] = True
                elif val == 'False':
                    mapped_query_params[key] = False
                elif key in ['limit', 'min_file_size', 'max_file_size']:
                    mapped_query_params[key] = int(val)
                else:
                    mapped_query_params[key] = val
            return mapped_query_params
        query_params_all_required_keys = add_missing_keys_with_defaults(query_params)
        mapped_query_params = map_query_params(query_params_all_required_keys)

    if args.available or (mapped_query_params and mapped_query_params['available']):
        show_filetypes(FILE_EXTENSIONS)
        return

    if args.threats or (mapped_query_params and mapped_query_params['threats']):
        show_filetypes(THREAT_EXTENSIONS)
        return

    if len(mapped_query_params):
        high_threat = check_threats(**mapped_query_params)
    else:
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

    if len(query_params):
        print("Processing CTDL with received Flask API endpoint Query Parameters: ", mapped_query_params, file=sys.stderr)
        validate_args(**mapped_query_params)
        download_content(**mapped_query_params)
    else:
        print("Processing CTDL with CLI Arguments: ", args_dict, file=sys.stderr)
        validate_args(**args_dict)
        download_content(**args_dict)


if __name__ == "__main__":
    main()
