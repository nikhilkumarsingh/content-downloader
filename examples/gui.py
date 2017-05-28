from appJar import gui
import sys

import site

def get_main_path():
    test_path = sys.path[0] # sys.path[0] is current path in 'examples' subdirectory
    split_on_char = "/"
    return split_on_char.join(test_path.split(split_on_char)[:-1])
main_path = get_main_path()
site.addsitedir(main_path+'/examples')
site.addsitedir(main_path+'/ctdl')
print ("Imported subfolder: %s" % (main_path+'/examples') )
print ("Imported subfolder: %s" % (main_path+'/ctdl') )

import ctdl
from ctdl.ctdl import main

# create gui and set title
app = gui("Content Search")

DEFAULT_QUERY_PARAMS = {
    'query': None,
    'file_type': 'pdf',
    'limit': 10,
    'directory': None,
    'parallel': False,
    'available': False,
    'threats': False,
    'min_file_size': 0,
    'max_file_size': -1,
    'no_redirects': False
}

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def valid_positive_int(s):
    if type(s) == int:
        return int(s) >= 0
    return False

def processContentSearch(btnName):
    if btnName == "Cancel":
        app.stop()
        return
    if not app.getEntry("queryEnt"):
        app.errorBox("Failed search", "Invalid query")
    elif app.getEntry("limitEnt") \
            and not valid_positive_int(app.getEntry("limitEnt")):
        app.errorBox("Failed search", "Limit must be integer")
    elif app.getEntry("minFileSizeEnt") \
            and not valid_positive_int(app.getEntry("minFileSizeEnt")):
        app.errorBox("Failed search", "Min File Size must be integer >= 0")
    elif app.getEntry("maxFileSizeEnt") \
            and not valid_positive_int(app.getEntry("maxFileSizeEnt")):
        app.errorBox("Failed search", "Max File Size must be integer >= 0")
    else:
        app.infoBox("Validated inputs", "Press OK to process downloads...")

        query_params = {}
        query_params["query"] = app.getEntry("queryEnt")
        query_params["file_type"] = app.getEntry("fileTypeEnt")
        query_params["limit"] = int(app.getEntry("limitEnt")) if app.getEntry("limitEnt") != "" else DEFAULT_QUERY_PARAMS["limit"]
        query_params["directory"] = app.getEntry("directoryEnt")
        query_params["parallel"] = app.getCheckBox("parallel-downloading")
        query_params["available"] = app.getCheckBox("show-available-formats")
        query_params["threats"] = app.getCheckBox("show-threat-formats")
        query_params["min_file_size"] = int(app.getEntry("minFileSizeEnt")) if app.getEntry("minFileSizeEnt") != "" else DEFAULT_QUERY_PARAMS["min_file_size"]
        query_params["max_file_size"] = int(app.getEntry("maxFileSizeEnt")) if app.getEntry("maxFileSizeEnt") != "" else DEFAULT_QUERY_PARAMS["max_file_size"]
        query_params["no_redirects"] = app.getCheckBox("toggle-redirects")

        main(query_params)

# http://appjar.info/pythonWidgets/

# add labels and entries in correct row & column
app.addLabel("queryLab", "Search Query:", 0, 0)
app.addEntry("queryEnt", 0, 1)
app.setEntryDefault("queryEnt", "i.e. python algorithms")
app.addLabel("fileTypeLab", "File Type:", 1, 0)
app.addEntry("fileTypeEnt", 1, 1)
app.setEntryDefault("fileTypeEnt", DEFAULT_QUERY_PARAMS["file_type"])
app.addLabel("limitLab", "Limit of Downloads:", 2, 0)
app.addEntry("limitEnt", 2, 1)
app.setEntryDefault("limitEnt", DEFAULT_QUERY_PARAMS["limit"])
app.addLabel("directoryLab", "Download Directory:", 3, 0)
app.addEntry("directoryEnt", 3, 1)
app.addLabel("parallelLab", "Parallel Downloading:", 4, 0)
app.addCheckBox("parallel-downloading", 4, 1)
app.addLabel("availableLab", "Log Available Formats:", 5, 0)
app.addCheckBox("show-available-formats", 5, 1)
app.addLabel("threatsLab", "Log Threat Formats:", 6, 0)
app.addCheckBox("show-threat-formats", 6, 1)
app.addLabel("minFileSizeLab", "Min File Size:", 7, 0)
app.addEntry("minFileSizeEnt", 7, 1)
app.setEntryDefault("minFileSizeEnt", DEFAULT_QUERY_PARAMS["min_file_size"])
app.addLabel("maxFileSizeLab", "Max File Size:", 8, 0)
app.addEntry("maxFileSizeEnt", 8, 1)
app.setEntryDefault("maxFileSizeEnt", "unlimited")
app.addLabel("redirectsLab", "URL Redirects:", 9, 0)
app.addCheckBox("toggle-redirects", 9, 1)

# changed this line to call a function
app.addButtons( ["Search", "Cancel"], processContentSearch, colspan=2)

# add some enhancements
app.setFocus("directoryEnt")
app.enableEnter(processContentSearch)

# start the GUI
app.go()