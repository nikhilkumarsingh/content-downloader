from appJar import gui
import sys
import random

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

from ctdl.utils import DEFAULT_ARGS, FILE_EXTENSIONS, THREAT_EXTENSIONS


import ctdl
from ctdl.ctdl import main
from ctdl import settings

# initialise globals for progress bar
settings.init_globals()

def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()

def valid_positive_int(s):
    if all(i.isdigit() for i in s): # check is int not float
        return int(s) >= 0
    return False

def get_threat_extensions():
    threat_extensions = []
    for k, v in THREAT_EXTENSIONS.items():
        threat_extensions.append(v)
    threat_extensions = [x[0] for x in threat_extensions] # flatten
    return threat_extensions

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
        query_params = {}
        query_params["query"] = app.getEntry("queryEnt")
        query_params["file_type"] = app.getOptionBox("file-type") if app.getOptionBox("file-type") and app.getOptionBox("file-type") != "" else DEFAULT_ARGS["file_type"]
        query_params["limit"] = int(app.getEntry("limitEnt")) if app.getEntry("limitEnt") != "" else DEFAULT_ARGS["limit"]
        if not app.getEntry("directoryEnt"):
            query_params['directory'] = app.getEntry("queryEnt").replace(' ', '-')
        else:
            query_params["directory"] = app.getEntry("directoryEnt")
        query_params["parallel"] = app.getCheckBox("parallel-downloading")
        query_params["available"] = DEFAULT_ARGS["available"]
        query_params["threats"] = DEFAULT_ARGS["threats"]
        query_params["min_file_size"] = int(app.getEntry("minFileSizeEnt")) if app.getEntry("minFileSizeEnt") != "" else DEFAULT_ARGS["min_file_size"]
        query_params["max_file_size"] = int(app.getEntry("maxFileSizeEnt")) if app.getEntry("maxFileSizeEnt") != "" else DEFAULT_ARGS["max_file_size"]
        query_params["no_redirects"] = app.getCheckBox("toggle-redirects")

        app.setFont(12)
        message = """Downloaded {0} {1} files on topic {2} and saving to directory: {3}.
        """.format(query_params["limit"],query_params["file_type"],query_params["query"],query_params["directory"])

        try:
            app.addMessage("mess", message)
        except:
            app.clearMessage("mess")
            app.setMessage("mess", message)

        # Optional prompt
        # if query_params["file_type"] in get_threat_extensions():
        #     app.infoBox("Validated inputs", "WARNING: High risk file type selected, press OK to continue...")

        main(query_params)

# http://appjar.info/pythonWidgets/

# create gui and set title
app = gui()
app.setTitle("Content Search")
# import sys; app.setBgImage(sys.path[0] + "/images/bg.gif")
app.setTransparency(100)
app.setFont(12, "Arial bold")
app.setBg("#FFFFFF")
app.setGeometry(400, 400)
app.setResizable(canResize=True)
# app.setLocation(0, 0)
app.setGuiPadding(10, 10)

def gen_hex_colour_code():
    return ''.join([random.choice('0123456789ABCDEF') for x in range(6)])

def change_theme(arg):
    hex_code = gen_hex_colour_code()
    app.setBg("#" + hex_code)

is_full_screen = False
def change_window_size(arg):
    global is_full_screen
    if not is_full_screen:
        app.setFont(30)
        app.setGeometry("fullscreen")
        app.setButton("Full Screen", "Normal Screen")
        is_full_screen = True
    else:
        app.setFont(12)
        app.setGeometry(400, 400)
        app.setButton("Full Screen", "Full Screen")
        is_full_screen = False

# add labels and entries in correct row & column
app.addFlashLabel("queryLab", "Search Query:", 0, 0)
app.addEntry("queryEnt", 0, 1)
app.setEntryDefault("queryEnt", "i.e. python algorithms")
app.addLabel("fileTypeLab", "File Type:", 1, 0)

def get_labelled_options():
    # dict with key categories with array values of associated file extensions
    labelled_dict = {}
    for k1, v1 in sorted(FILE_EXTENSIONS.items()):
        labelled_dict[k1] = []
        for k2, v2 in sorted(v1.items()):
            labelled_dict[k1].append(v2)

    # array appended with specially formatted categories followed by associated file extensions
    labelled_arr = []
    for k1, v1 in labelled_dict.items():
        labelled_arr.append(("-- " + k1 + " --"))
        for i, el in enumerate(v1):
            labelled_arr.append(el)
    return labelled_arr

app.addLabelOptionBox("file-type", get_labelled_options(), 1, 1)

app.addLabel("limitLab", "Limit of Downloads:", 3, 0)
app.setLabelBg("queryLab", "#EEEEFF")
app.addEntry("limitEnt", 3, 1)
app.setEntryDefault("limitEnt", DEFAULT_ARGS["limit"])
app.addLabel("directoryLab", "Download Directory Name:", 4, 0)
app.addEntry("directoryEnt", 4, 1)
app.addLabel("parallelLab", "Parallel Downloading:", 5, 0)
app.addCheckBox("parallel-downloading", 5, 1)
app.addLabel("minFileSizeLab", "Minimum File Size:", 6, 0)
app.addEntry("minFileSizeEnt", 6, 1)
app.setEntryDefault("minFileSizeEnt", DEFAULT_ARGS["min_file_size"])
app.addLabel("maxFileSizeLab", "Maximum File Size:", 7, 0)
app.addEntry("maxFileSizeEnt", 7, 1)
app.setEntryDefault("maxFileSizeEnt", "unlimited")
app.addLabel("redirectsLab", "URL Redirects:", 8, 0)
app.addCheckBox("toggle-redirects", 8, 1)
app.addHorizontalSeparator(9, 0, 2, colour="red")
app.addButtons( ["Search", "Cancel"], processContentSearch, colspan=2)
app.setButtonImage("Search", sys.path[0] + "/images/search_button.gif")
app.setButtonImage("Cancel", sys.path[0] + "/images/cancel_button.gif")
app.addButton("Full Screen", change_window_size, 11, 0)
app.addButton("Switch Theme", change_theme, 11, 1)
app.addButtons(["English", "Hindi", "Deutsch", "Espanol", "Mandarin"], app.changeLanguage, colspan=5)
app.addWebLink("Suggestions or issues?", "https://github.com/nikhilkumarsingh/content-downloader/issues", colspan=2)
app.addMeter("progress", colspan=2)
app.setMeterFill("progress", "blue")

def updateMeter():
    app.setMeter("progress", settings.urls_percent_complete)
updateMeter()
# schedule function to be called regularly
app.registerEvent(updateMeter)

# add some enhancements
app.setFocus("queryEnt")
app.enableEnter(processContentSearch)

# start the GUI
# internationalisation http://appjar.info/pythonInternationalisation/#internationalisation
app.go("english") # starting internationalisation language