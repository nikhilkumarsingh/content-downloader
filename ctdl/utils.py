DEFAULT_ARGS = {
    "query": None,
    "file_type": 'pdf',
    "limit": 10,
    "directory": None,
    "parallel": False,
    "available": False,
    "threats": False,
    "min_file_size": 0,
    "max_file_size": -1,
    "no_redirects": False
}

FILE_EXTENSIONS = {
    'Adobe Flash':'swf',
    'Adobe Portable Document Format':'pdf',
    'Adobe PostScript':'ps',
    'Autodesk Design Web Format': 'dwf',
    'Google Earth': 'kml',
    'XML': 'xml',
    'Microsoft PowerPoint': 'ppt',
    'Microsoft Excel': 'xls',
    'Microsoft Word': 'doc',
    'GPS eXchange Format': 'gpx',
    'Hancom Hanword': 'hwp',
    'HTML': 'html',
    'OpenOffice presentation': 'odp',
    'OpenOffice spreadsheet': 'ods',
    'OpenOffice text': 'odt',
    'Rich Text Format': 'rtf',
    'Scalable Vector Graphics': 'svg',
    'TeX/LaTeX': 'tex',
    'Text': 'txt',
    'Basic source code': 'bas',
    'C source code': 'c',
    'C++ source code': 'cpp',
    'C# source code': 'cs',
    'Java source code': 'java',
    'Perl source code': 'pl',
    'Python source code': 'py',
    'Wireless Markup Languag': 'wml'
}

THREAT_EXTENSIONS = {
    'Executable files': ['exe','com'],
    'Program information file': 'pif',
    'Screensaver file': 'scr',
    'Visual Basic script': 'vbs',
    'Shell scrap file': 'shs',
    'Microsoft Compiled HTML Help': 'chm',
    'Batch file': 'bat'
}