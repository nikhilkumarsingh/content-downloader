import os
import threading
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

try:
	from Tkinter import *
except :
	from tkinter import *

try:
	import ttk
except :
	from tkinter import ttk

chunk_size = 1024
parallel = False
exit_flag = 0
file_name = []
total_chunks = []
i_max = []

s = requests.Session()
# Max retries and back-off strategy so all requests to http:// sleep before retrying
retries = Retry(total = 5, 
				backoff_factor = 0.1, 
				status_forcelist = [500,  502,  503,  504])
s.mount('http://', HTTPAdapter(max_retries = retries))


def download(urls, directory, idx, min_file_size = 0, max_file_size = -1,  
			 no_redirects = False, pos = 0, mode = 's'):
	"""
	download function for serial download
	"""
	global main_it
	global exit_flag
	global total_chunks
	global file_name
	global i_max

	# loop in single thread to serialize downloads
	for url in urls:
		file_name[idx] = url.split( '/')[-1] 
		file_address = directory + '/' + file_name[idx]
		is_redirects = not no_redirects

		resp = s.get(url, stream = True, allow_redirects = is_redirects)
		if not resp.status_code == 200:
			# ignore this file since server returns invalid response
			return
		try:
			total_size = int(resp.headers['content-length'])
		except KeyError:
			total_size = len(resp.content)

		total_chunks[idx] = total_size / chunk_size
		if total_chunks[idx] < min_file_size: 
			# ignore this file since file size is lesser than min_file_size
			continue
		elif max_file_size != -1 and total_chunks[idx] > max_file_size:
			# ignore this file since file size is greater than max_file_size
			continue

		file_iterable = resp.iter_content(chunk_size = chunk_size)
		with open(file_address, 'wb') as f:
			for sno, data in enumerate(file_iterable):
				i_max[idx] = sno + 1
				f.write(data)

	exit_flag += 1


def download_parallel(url, directory, idx, min_file_size = 0, max_file_size = -1,  
			 no_redirects = False, pos = 0, mode = 's'):
	"""
	download function to download parallely
	"""
	global main_it
	global exit_flag
	global total_chunks
	global file_name
	global i_max

	file_name[idx]= url.split('/')[-1] 
	file_address = directory + '/' + file_name[idx]
	is_redirects = not no_redirects

	resp = s.get(url, stream = True, allow_redirects = is_redirects)
	if not resp.status_code == 200:
		# ignore this file since server returns invalid response
		return
	try:
		total_size = int(resp.headers['content-length'])
	except KeyError:
		total_size = len(resp.content)

	total_chunks[idx] = total_size / chunk_size
	if total_chunks[idx] < min_file_size: 
		# ignore this file since file size is lesser than min_file_size
		exit_flag += 1
		return
	elif max_file_size != -1 and total_chunks[idx] > max_file_size:
		# ignore this file since file size is greater than max_file_size
		exit_flag += 1
		return

	file_iterable = resp.iter_content(chunk_size = chunk_size)
	with open(file_address, 'wb') as f:
		for sno, data in enumerate(file_iterable):
			i_max[idx] = sno + 1
			f.write(data)
	
	exit_flag += 1



class myThread (threading.Thread):
	"""
	custom thread to run download thread
	"""
	def __init__(self, url, directory, idx, min_file_size, max_file_size, no_redirects):
		threading.Thread.__init__(self)
		self.idx = idx
		self.url = url
		self.directory = directory
		self.min_file_size = min_file_size
		self.max_file_size = max_file_size
		self.no_redirects = no_redirects


	def run(self):
		"""
		function called when thread is started
		"""
		global parallel

		if parallel:
			download_parallel(self.url, self.directory, self.idx, 
							  self.min_file_size, self.max_file_size, self.no_redirects)
		else:
			download(self.url, self.directory, self.idx,  
					 self.min_file_size, self.max_file_size, self.no_redirects)


class progress_class():
	"""
	custom class for profress bar
	"""
	def __init__(self, frame, url, directory, min_file_size, max_file_size, no_redirects):
		global i_max
		global file_name
		global parallel

		self.url = url
		self.directory = directory
		self.min_file_size = min_file_size
		self.max_file_size = max_file_size
		self.no_redirects = no_redirects
		self.frame = frame

		self.progress = []
		self.str = []
		self.label = []
		self.bytes = []
		self.maxbytes = []
		self.thread = []

		if parallel:
			self.length = len(self.url) 
		else:
			# to serialize just make a single thread
			self.length = 1 

		# for parallel downloading
		for self.i in range(0, self.length):
			file_name.append("")
			i_max.append(0)
			total_chunks.append(0)

			# initialize progressbar
			self.progress.append(ttk.Progressbar(frame, orient="horizontal", 
								 length=300, mode="determinate"))
			self.progress[self.i].pack()
			self.str.append(StringVar())
			self.label.append(Label(frame, textvariable=self.str[self.i], width=40))
			self.label[self.i].pack()
			self.progress[self.i]["value"] = 0
			self.bytes.append(0)
			self.maxbytes.append(0)

		# start thread
		self.start()


	def start(self):
		"""
		function to initialize thread for downloading
		"""
		global parallel
		for self.i in range(0, self.length):
			if parallel:
				self.thread.append(myThread(self.url[ self.i ], self.directory, self.i, 
								   self.min_file_size, self.max_file_size, self.no_redirects))
			else:
				# if not parallel whole url list is passed
				self.thread.append(myThread(self.url, self.directory, self.i , self.min_file_size, 
								   self.max_file_size,  self.no_redirects))
			self.progress[self.i]["value"] = 0
			self.bytes[self.i] = 0
			self.thread[self.i].start()

		self.read_bytes()


	def read_bytes(self):
		"""
		reading bytes; update progress bar after 1 ms
		"""
		global exit_flag

		for self.i in range(0, self.length) :
			self.bytes[self.i] = i_max[self.i]
			self.maxbytes[self.i] = total_chunks[self.i]
			self.progress[self.i]["maximum"] = total_chunks[self.i]
			self.progress[self.i]["value"] = self.bytes[self.i]
			self.str[self.i].set(file_name[self.i]+ "       " + str(self.bytes[self.i]) 
								  + "KB / " + str(int(self.maxbytes[self.i] + 1)) + " KB")

		if exit_flag == self.length:
			exit_flag = 0
			self.frame.destroy()
		else:
			self.frame.after(10, self.read_bytes)


def download_parallel_gui(root, urls, directory, min_file_size, max_file_size, no_redirects):
	"""
	called when paralled downloading is true
	"""
	global parallel

	# create directory to save files
	if not os.path.exists(directory):
		os.makedirs(directory)
	parallel = True
	app = progress_class(root, urls, directory, min_file_size, max_file_size, no_redirects)




def download_series_gui(frame, urls, directory, min_file_size, max_file_size, no_redirects):
	"""
	called when user wants serial downloading
	"""

	# create directory to save files
	if not os.path.exists(directory):
		os.makedirs(directory)
	app = progress_class(frame, urls, directory, min_file_size, max_file_size, no_redirects)

 
