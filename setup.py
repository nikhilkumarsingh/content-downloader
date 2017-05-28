# -*- coding: utf-8 -*-
from setuptools import setup

def readme():
	try:
	    with open('README.rst') as f:
	        return f.read()
	except:
		pass

setup(name = 'ctdl',
      version = '1.4.6',
      classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
	    'Programming Language :: Python :: 2',
	    'Programming Language :: Python :: 2.6',
	    'Programming Language :: Python :: 2.7',
	    'Programming Language :: Python :: 3',
	    'Programming Language :: Python :: 3.3',
	    'Programming Language :: Python :: 3.4',
	    'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
      ],
      keywords = 'content downloader bulk files',
      description = 'Bulk file downloader on any topic.',
      long_description = readme(),
      url = 'https://github.com/nikhilkumarsingh/content-downloader',
      author = 'Nikhil Kumar Singh',
      author_email = 'nikhilksingh97@gmail.com',
      license = 'MIT',
      packages = ['ctdl'],
      install_requires = ['requests', 'bs4', 'lxml', 'tqdm'],
      dependency_links = ['git+https://github.com/nikhilkumarsingh/tqdm'],
      include_package_data = True,
      entry_points="""
      [console_scripts]
      ctdl = ctdl.ctdl:main
      """,
      zip_safe = False)
