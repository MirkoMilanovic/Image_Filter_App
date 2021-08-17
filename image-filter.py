"""
This is a program for filtering images by keywords and date of creation:
"""

from tkinter import *
from tkinter import filedialog
import subprocess
import os
import iptcinfo3
import win32com.client
from PIL import Image, ImageTk
import ast
import logging


iptcinfo_logger = logging.getLogger('iptcinfo')
iptcinfo_logger.setLevel(logging.ERROR)

class Window:
    def __init__(self, window):

        self.image_list = []
        self.image_fullpath_list = []
        self.lastselectionList = []
        self.value = ''
        self.keywords_list = []
        self.previewed_image_fullpath = ''
        self.all_images_metadata_dict = {}
        self.recquired_metadata = []
        self.default_directory = open("default_directory.txt", "r").read().replace('\\', '/')


        # Keywords
        self.l1 = Label(window, text="Keywords:", font=("Calibri bold", 13))
        self.l1.grid(row=1, column=1, sticky=W+S, padx=(15, 0))
        
        self.keywords = StringVar()
        self.e1 = Entry(window, textvariable=self.keywords, width=45, font=("Calibri Bold", 13), fg='#993399')
        self.e1.grid(row=2, column=1, sticky=N+E+W, padx=(15, 5))

        # Date created
        self.l9 = Label(window, text="Created (MM.YYYY or YYYY):", font=("Calibri bold", 13))
        self.l9.grid(row=3, column=1, sticky=W, pady=10, padx=(15, 0))
        
        self.created = StringVar()
        self.e2 = Entry(window, textvariable=self.created, width=17, font=("Calibri Bold", 13), fg='#993399', justify='right')
        self.e2.grid(row=3, column=1, sticky=W, padx=(240, 0))

        # Label - search results
        self.l2 = Label(window, text="Search results: ", font=("Calibri Bold", 13))
        self.l2.grid(row=0, column=0, sticky=W+S, padx=5)

        # Label - open image in Explorer
        self.l3 = Label(window, text="Find previewed image in Explorer:", font=("Calibri Bold", 13))
        self.l3.grid(row=15, column=1, sticky=E, padx=(0, 70))

        # Label - open with Photoshop
        self.l4 = Label(window, text="Open selected images with Photoshop:", font=("Calibri Bold", 13))
        self.l4.grid(row=16, column=1, sticky=E, padx=(0, 70))

        # List of images
        self.l5 = Label(window, text="Search for images:", font=("Calibri Bold", 13))
        self.l5.grid(row=5, column=1, sticky=E, padx=(0, 70))

        self.list1 = Listbox(window, width=30, selectmode=EXTENDED, font=("Calibri Bold", 12), fg='#993399')
        self.list1.grid(row=1, column=0, rowspan=15, padx=5, sticky=N+S+E+W)

        # Scrollbar y-axis
        self.sb1 = Scrollbar(window)
        self.sb1.grid(row=1, column=0, rowspan=15, sticky=N+S+E)

        self.list1.configure(yscrollcommand=self.sb1.set)
        self.sb1.configure(command=self.list1.yview)

        # Scrollbar x-axis
        self.sb2 = Scrollbar(window, orient=HORIZONTAL)
        self.sb2.grid(row=16, column=0, sticky=EW+N)

        self.list1.configure(xscrollcommand=self.sb2.set)
        self.sb2.configure(command=self.list1.xview)

        # Label - working directory
        self.folder_path = StringVar(value=self.default_directory)
        self.directory = self.folder_path.get()
        self.l6 = Label(master=window, textvariable=self.folder_path, font=("Calibri Bold", 12), fg='#993399', anchor="e", justify=RIGHT)
        self.l6.grid(row=0, column=1, sticky=E+W, padx=(0, 70))

        # Label - image preview
        self.l7 = Label(window, text="Image preview:", font=("Calibri Bold", 13))
        self.l7.grid(row=6, column=1, sticky=W+S, padx=15)

        # Label - image count
        self.image_count = StringVar(value='No results')
        self.l8 = Label(window, textvariable=self.image_count, font=("Calibri Bold", 12), fg='#993399')
        self.l8.grid(row=16, column=0, sticky=W+S, padx=5)

        self.img_start = Image.open('img/camera-image.png')
        self.tkimage_start = ImageTk.PhotoImage(self.img_start)
        self.l10 = Label(window, image=self.tkimage_start)
        self.l10.grid(row=7, column=1)

        self.l11 = Label(window, text='', anchor="w", fg='#993399', font=("Arial Bold", 12), justify=RIGHT)
        self.l11.grid(row=6, column=1, sticky=W+E, padx=(140, 5))


        # Button - directory
        self.dir_icon = Image.open("img/directory-icon.png")
        self.dir_icon_render = ImageTk.PhotoImage(self.dir_icon)
        self.b1 = Button(window, image=self.dir_icon_render, width=45, command=self.browse_directory)
        self.b1.grid(row=0, column=1, sticky=E, padx=5, pady=2)

        # Button - search
        self.search_icon = Image.open("img/search-icon.png")
        self.search_icon_render = ImageTk.PhotoImage(self.search_icon)
        self.b2 = Button(window, image=self.search_icon_render, width=45, command=self.search_images)
        self.b2.grid(row=5, column=1, sticky=E, padx=5, pady=2)

        # Button - explorer
        self.explorer_icon = Image.open("img/explorer-icon.png")
        self.explorer_icon_render = ImageTk.PhotoImage(self.explorer_icon)
        self.b3 = Button(window, image=self.explorer_icon_render, width=45, command=self.image_in_explorer)
        self.b3.grid(row=15, column=1, sticky=E, padx=5, pady=2)

        # Button - photoshop
        self.photoshop_icon = Image.open("img/photoshop-icon.png")
        self.photoshop_icon_render = ImageTk.PhotoImage(self.photoshop_icon)
        self.b4 = Button(window, image=self.photoshop_icon_render, width=45, command=self.open_photoshop)
        self.b4.grid(row=16, column=1, sticky=E, padx=5, pady=2)

        # Program name
        window.wm_title("Image filtering by Mirko M.")

        # Resizable grid
        window.grid_columnconfigure(1,weight=1)
        window.grid_rowconfigure(7,weight=1)

        # Show selected image and label
        self.list1.bind("<<ListboxSelect>>", self.on_select)

        # Create images metadata
        self.create_images_metadata()

        # Bind the Enter key with a search_images function
        window.bind('<Return>', self.search_images)
        

    def create_images_metadata(self):
        metadata_file = open("images_metadata.txt", "r+", encoding="utf-8")
        content = metadata_file.read()
        if content != '':
            self.all_images_metadata_dict = ast.literal_eval(content)
        else:
            pass
        
        def get_list_of_files(dirName):
            all_files_list = os.listdir(dirName)
            all_filepaths_list = []
            for entry in all_files_list:
                fullPath = os.path.join(dirName, entry).replace('\\', '/')
                if os.path.isdir(fullPath):
                    all_filepaths_list = all_filepaths_list + get_list_of_files(fullPath)
                else:
                    all_filepaths_list.append(fullPath)
            else:
                return all_filepaths_list

        self.directory = self.folder_path.get()

        # Delete unexistant files
        unexistant_files = []
        for image_path in self.all_images_metadata_dict.keys():
            if os.path.isfile(image_path):
                pass
            else:
                unexistant_files.append(image_path)

        for file in unexistant_files:    
            del self.all_images_metadata_dict[file]

        # Get the list of all files in directory tree at given path
        all_files_fullpath_list = get_list_of_files(self.directory)
        for file_fullpath in all_files_fullpath_list:
            if file_fullpath.upper().endswith(".JPG"):
                if file_fullpath in self.all_images_metadata_dict:
                    pass
                else:
                    try:
                        info = iptcinfo3.IPTCInfo(file_fullpath)
                        image_keywords_list = [i.decode('utf8') for i in info['keywords']]
                        date_taken = info['date created'].decode('utf8')
                        pic_year = date_taken[0:4]
                        pic_month = date_taken[4:6]

                        self.all_images_metadata_dict[file_fullpath] = pic_month+', '+pic_year+', '+", ".join(image_keywords_list)
                    except (AttributeError, TypeError):
                        pass
        metadata_file.seek(0)
        metadata_file.write(str(self.all_images_metadata_dict))
        metadata_file.truncate()
        metadata_file.close()

    def browse_directory(self):
        # Allow user to select a directory and store it in global var called folder_path
        filename = filedialog.askdirectory()
        if len(filename) == 0:
            filename = self.default_directory
        self.folder_path.set(filename)
        # Create images metadata
        self.create_images_metadata()

    def search_images(self, event=None):
        self.image_list.clear()
        self.image_fullpath_list.clear()

        self.keywords_list = self.e1.get().replace(";", " ").replace(",", " ").lower().split()
        self.date_of_creation = self.e2.get().replace(".", "").replace(",", "")

        date_year = '' + self.date_of_creation[-4:]
        date_month = '' + self.date_of_creation[-6:-4]

        self.recquired_metadata = self.keywords_list
        if date_year != '':
            self.recquired_metadata.append(date_year)
        
        if date_month != '':
            self.recquired_metadata.append(date_month)

        for image, keywords in self.all_images_metadata_dict.items():
            image_keywords = keywords.lower().replace(" ", "").split(',')
            if image.startswith(self.folder_path.get()+'/'):
                if os.path.isfile(image):
                    if (set(self.recquired_metadata)).issubset(set(image_keywords)):
                        self.image_list.append(image.split('/')[-1])
                        self.image_fullpath_list.append(image)
               
        self.list1.delete(0, END)
        for image in self.image_list:
            self.list1.insert(END, image)
        self.image_count.set("{ " + str(len(self.image_list)) + " images found }")

    def on_select(self, evt):
        active_image = self.list1.get(ANCHOR)
        active_image_path = ''
        for file_path in self.all_images_metadata_dict.keys():
            if file_path.endswith(active_image):
                active_image_path = file_path
        self.img = Image.open(active_image_path)
        self.img.thumbnail((500,400))
        self.tkimage = ImageTk.PhotoImage(self.img)
        self.l10['image'] = self.tkimage
        self.l11['text'] = active_image

    def image_in_explorer(self):
        selection = self.list1.curselection()
        for i in selection:
            path = self.image_fullpath_list[i].replace("/", "\\")
            subprocess.Popen('explorer /select,' + path)

    def open_photoshop(self):
        psApp = win32com.client.Dispatch("Photoshop.Application")
        selection = self.list1.curselection()
        for i in selection:
            psApp.Open(self.image_fullpath_list[i])

window = Tk()
window.geometry("900x900")
Window(window)
window.mainloop()
