import os
import requests
from tqdm import tqdm

chunk_size = 1024

def download(url, directory):
	file_name = url.split('/')[-1]
	file_address = directory + '/' + file_name

	resp = requests.get(url, stream = True)
	try:
		total_size = int(resp.headers['content-length'])
	except KeyError:
		total_size = len(resp.content)

	total_chunks = total_size/chunk_size
	file_iterable = resp.iter_content(chunk_size = chunk_size)

	print("Downloading {}".format(file_name))
	
	with open(file_address, 'wb') as f:
		for data in tqdm(iterable = file_iterable, total = total_chunks, unit = 'KB'):
			f.write(data)

	print("{} has been saved to {}\n".format(file_name, file_address))


def download_all(urls, directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

	for url in urls:
		download(url, directory)



