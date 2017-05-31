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
    'text': {
        'Adobe Portable Document Format': 'pdf',
        'Microsoft PowerPoint': 'ppt',
        'Microsoft Excel': 'xls',
        'Microsoft Word': 'doc',
        'OpenOffice presentation': 'odp',
        'OpenOffice spreadsheet': 'ods',
        'OpenOffice text': 'odt',
        'Rich Text Format': 'rtf',
        'Adobe PostScript': 'ps',
        'Hancom Hanword': 'hwp',
        'TeX/LaTeX': 'tex',
        'Text': 'txt',
    },
    'media': {
        'Adobe Flash':'swf',
        'Scalable Vector Graphics': 'svg',
    },
    'cad': {
        'Autodesk Design Web Format': 'dwf',
    },
    'data': {
        'Google Earth': 'kml',
        'XML': 'xml',
        'GPS eXchange Format': 'gpx',
        'Wireless Markup Language': 'wml'
    },
    'code': {
        'HTML': 'html',
        'Basic source code': 'bas',
        'C source code': 'c',
        'C++ source code': 'cpp',
        'C# source code': 'cs',
        'Java source code': 'java',
        'Perl source code': 'pl',
        'Python source code': 'py',
        'Ruby source code': 'rb',
        'Rust source code': 'rs',
        'JavaScript source code': 'js'
    }
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