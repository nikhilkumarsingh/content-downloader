from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from utils import FILE_EXTENSIONS, THREAT_EXTENSIONS
from tkinter.messagebox import *
import os
import threading
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from tqdm import tqdm, trange

import tkinter as tk

from gui_download import *
from ctdl import *

root = Tk()


def download_content_gui(**args):
    """
    main function to fetch links and download them
    """
    if not args['directory']:
        args['directory'] = args['query'].replace(' ', '-')

    print("Downloading {0} {1} files on topic {2} and saving to directory: {3}"
        .format(args['limit'], args['file_type'], args['query'], args['directory']))

    links = search(args['query'], args['file_type'], args['limit'])


    if args['parallel']:
        download_parallel_gui(root,links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])
    else:
        download_series_gui(root,links, args['directory'], args['min_file_size'], args['max_file_size'], args['no_redirects'])



fields = 'Search query', 'Min Allowed File Size', 'Max Allowed File Size', 'Download Directory','Limit'
args={'parallel': False, 'file_type': 'pdf', 'threats': False, 'no_redirects': False, 'available': False, 'query': 'python',
     'min_file_size': 0, 'max_file_size': -1, 'directory': None, 'limit': 10}



class makeform:
    global args
    def __init__(self,root):
        self.row0 = Frame(root)
        self.lab0 = Label(self.row0, width=25, text=fields[0], anchor='w')
        self.entry_query = Entry(self.row0)
        self.entry_query.insert(0, 'python')
        self.entry_query.bind('<FocusIn>', self.on_entry_click)
        self.entry_query.bind('<FocusOut>', self.on_focusout)
        self.entry_query.config(fg = 'grey')
        self.row0.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab0.pack(side=LEFT)
        self.entry_query.pack(side=RIGHT, expand=YES, fill=X)


        self.row1 = Frame(root)
        self.lab1 = Label(self.row1, width=25, text=fields[1], anchor='w')
        self.entry_min = Entry(self.row1)
        self.entry_min.insert(0, '0')
        self.entry_min.bind('<FocusIn>', self.on_entry_click)
        self.entry_min.bind('<FocusOut>', self.on_focusout)
        self.entry_min.config(fg = 'grey')
        self.row1.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab1.pack(side=LEFT)
        self.entry_min.pack(side=RIGHT, expand=YES, fill=X)


        self.row2 = Frame(root)
        self.lab2 = Label(self.row2, width=25, text=fields[2], anchor='w')
        self.entry_max = Entry(self.row2)
        self.entry_max.insert(0, '-1')
        self.entry_max.bind('<FocusIn>', self.on_entry_click)
        self.entry_max.bind('<FocusOut>', self.on_focusout)
        self.entry_max.config(fg = 'grey')
        self.row2.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab2.pack(side=LEFT)
        self.entry_max.pack(side=RIGHT, expand=YES, fill=X)

        self.dir_text = StringVar()
        self.dir_text.set('Choose Directory')
        self.row3 = Frame(root)
        self.lab3 = Label(self.row3, width=25, text=fields[3], anchor='w')
        self.entry_dir = Button(self.row3,textvariable=self.dir_text,command=self.ask_dir)
        self.row3.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab3.pack(side=LEFT)
        self.entry_dir.pack(side=RIGHT, expand=YES, fill=X)
        self.dir_opt = options = {}
        options['initialdir'] = 'C:\\'
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = 'This is a title'


        self.row4 = Frame(root)
        self.lab4 = Label(self.row4, width=25, text=fields[4], anchor='w')
        self.entry_limit = Entry(self.row4)
        self.entry_limit.insert(0, '10')
        self.entry_limit.bind('<FocusIn>', self.on_entry_click)
        self.entry_limit.bind('<FocusOut>', self.on_focusout)
        self.entry_limit.config(fg = 'grey')
        self.row4.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab4.pack(side=LEFT)
        self.entry_limit.pack(side=RIGHT, expand=YES, fill=X)

        self.choiceVar = StringVar()
        self.choices = []
        for val in THREAT_EXTENSIONS.values():
            if type(val) == list:
                for el in val:
                        self.choices.append(el)
            else:
                self.choices.append(val)

        for val in FILE_EXTENSIONS.values():
            if type(val) == list:
                for el in val:
                        self.choices.append(el)
            else:
                self.choices.append(val)
        self.choiceVar.set('pdf')

        self.row5 = Frame(root)
        self.lab = Label(self.row5, width=25, text="File Type", anchor='w')
        self.optionmenu = ttk.Combobox(self.row5, textvariable=self.choiceVar, values=self.choices)
        self.row5.pack(side=TOP, fill=X, padx=5, pady=5)
        self.lab.pack(side=LEFT)
        self.optionmenu.pack(side=RIGHT, expand=YES, fill=X)

        self.row6=Frame(root)
        self.p= BooleanVar()
        Checkbutton(self.row6, text="parallel downloading", variable=self.p).pack(side=LEFT)
        self.t=BooleanVar()
        Checkbutton(self.row6, text="toggle redirects", variable=self.t).pack(side=LEFT)
        self.row6.pack(side=TOP, fill=X, padx=5, pady=5)

        self.row7=Frame(root)
        self.search_button = Button(self.row7, width=15, text="Download", anchor='w')
        self.search_button.bind('<Button-1>',self.click_download)
        self.row7.pack(side=TOP, fill=X, padx=5, pady=5)
        self.search_button.pack(side=LEFT)


    def click_download(self,event):
        args['parallel']=self.p.get()
        args['filetype']=self.optionmenu.get()
        args['no_redirects']=self.t.get()
        args['query']=self.entry_query.get()
        args['min_file_size']=int(self.entry_min.get())
        args['max_file_size']=int(self.entry_max.get())
        args['limit']=int(self.entry_limit.get())
        print(args)
        self.check_threat()
        download_content_gui(**args)


    def on_entry_click(self,event):
        """function that gets called whenever entry is clicked"""
        if event.widget.config('fg')[4] == 'grey':
           event.widget.delete(0, "end") # delete all the text in the entry
           event.widget.insert(0, '') #Insert blank for user input
           event.widget.config(fg = 'black')

    def on_focusout(self,event):
        if event.widget.get() == '':
            event.widget.insert(0, '')
            event.widget.config(fg = 'grey')

    def check_threat(self):
        """
        function to check input filetype against threat extensions list 
        """
        is_high_threat = False
        for val in THREAT_EXTENSIONS.values():
            if type(val) == list:
                for el in val:
                    if self.optionmenu.get() == el:
                        is_high_threat = True
                        break
            else:
                if self.optionmenu.get() == val:
                    is_high_threat = True
                    break

        if is_high_threat==True:
            is_high_threat=not askokcancel('FILE TYPE', 'WARNING: Downloading this file type may expose you to a \
                heightened security risk.\nPress "OK" to proceed or "CANCEL" to exit')
        return not is_high_threat

    def ask_dir(self):
        args['directory']=filedialog.askdirectory(**self.dir_opt) 
        self.dir_text.set(args['directory'])



# class SampleApp(Tk):

#     def __init__(self):
#         Tk.__init__(self)
#         self.button = Button(self,text="start", command=self.start)
#         self.button.pack(fill=X)
#         self.progress = ttk.Progressbar(self, orient="horizontal",
#                                         length=300, mode="determinate")
#         self.progress.pack()
#         self.bytes = 0
#         self.maxbytes = 0

#     def start(self):
#         self.progress["value"] = 0
#         self.maxbytes = 50000
#         self.progress["maximum"] = 50000
#         self.read_bytes()

#     def read_bytes(self):
#         '''simulate reading 500 bytes; update progress bar'''
#         self.bytes += 500
#         self.progress["value"] = self.bytes
#         if self.bytes < self.maxbytes:
#             # read more bytes after 100 ms
#             self.after(100, self.read_bytes)


def main():


    # app = SampleApp()

    s=ttk.Style()
    s.theme_use('clam')
    ents = makeform(root)



    # root.bind('<Return>', (lambda event, e=ents: fetch(e)))   
    # b1 = Button(root, text='Show',
    #       command=(lambda e=ents: fetch(e)))
    # b1.pack(side=LEFT, padx=5, pady=5)
    # b2 = Button(root, text='Quit', command=root.quit)
    # b2.pack(side=LEFT, padx=5, pady=5)
    root.mainloop()

    # app.mainloop()

    # mainloop()


if __name__ == "__main__":
    main()
