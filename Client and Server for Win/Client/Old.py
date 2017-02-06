import tkinter as tk
from tkinter import ttk
import os
import cv2
import numpy
import imutils
import PIL
from PIL import Image
from PIL import ImageTk

path = os.getcwd()
LARGE_FONT = ("Verdana", 12)
var = False


class SecondYearProjectClient():

    def __init__(self, *args, **kwargs):
        self.master = tk.Tk()
        self.master.wm_title("Client")
        self.master.geometry("{0}x{1}+0+0".format(1360, 768))

        self.container = tk.Frame(self.master, width=1360, height=768, bg="black")
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.lblAd = None

        btnStart = ttk.Button(self.container, text="Start", command=lambda: self.Play_Ad())
        btnStart.pack()

        #self.frames = {}
        #for F in (EventInfo, TimeTable):
        #    frame = F(container, self)
        #    self.frames[F] = frame
        #    frame.grid(row=0, column=0, sticky="nsew")

        #btnLeft = tk.Button(self, text="<<<", command=lambda: self.show_frame(TimeTable), height=10)
        btnLeft = tk.Button(self.container, text="<<<")
        btnLeft.bind("<Button-1>", self.Show_TimeTable)
        btnLeft.pack(side="left")

        #btnRight = tk.Button(self, text=">>>", command=lambda: self.show_frame(EventInfo), height=10)
        btnRight = tk.Button(self.container, text=">>>")
        btnRight.bind("<Button-1>", self.Show_EventInfo)
        btnRight.pack(side="right")

    def update(self):
        ad_path = path + "/ads/anger/anger02.mp4"
        print(ad_path)
        cap = cv2.VideoCapture(ad_path)
        while True:
            _, frame = cap.read()
            image = imutils.resize(frame, width=1360, height=768)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = PIL.Image.fromarray(image)
            image = ImageTk.PhotoImage(image)

            if self.lblAd is None:
                self.lblAd = tk.Label(self.container, width=1360, height=768, image=image)
                self.lblAd.image = image
                self.lblAd.place(x=0, y=0)
            else:
                self.lblAd.configure(image=image)
                self.lblAd.image = image

    def Show_TimeTable(self):
        #frame = self.frames[TimeTable]
        frame = TimeTable
        frame.tkraise()

    def Show_EventInfo(self):
        #frame = self.frames[EventInfo]
        frame = EventInfo
        frame.tkraise()


class TimeTable(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,  bg="blue")
        lblTitle = ttk.Label(self, text="Time Table", font=LARGE_FONT)
        lblTitle.pack(pady=10, padx=10)

        self.lblAd = None

        btnLeft = tk.Button(self, text="<<<", command=lambda: controller.show_frame(EventInfo), height=10)
        btnLeft.pack(side="left")

        self.Load_Image(controller)

    def Load_Image(self, controller):
        image_path = path + "/event_info/info2.jpg"
        image = cv2.imread(image_path)
        image = imutils.resize(image, width=1360, height=768)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.lblAd = tk.Label(self, width=1360, height=768, image=image)
        self.lblAd.image = image
        self.lblAd.place(x=0, y=0)

        btnLeft = tk.Button(self, text="<<<", command=lambda: controller.show_frame(EventInfo), height=10)
        btnLeft.pack(side="left")

class EventInfo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,  bg="red")
        lblTitle = ttk.Label(self, text="Event Info", font=LARGE_FONT)
        lblTitle.pack(pady=10, padx=10)

        self.lblAd = None
        self.btnRight = tk.Button(self, text=">>>", command=lambda: controller.show_frame(TimeTable), height=10)
        self.btnRight.pack(side="right")

        self.Load_Image(controller)

    def Load_Image(self, controller):
        image_path = path + "/event_info/event_info.jpg"
        print(image_path)
        image = cv2.imread(image_path)
        image = imutils.resize(image, width=1360, height=768)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.lblAd = tk.Label(self, width=1360, height=768, image=image)
        self.lblAd.image = image
        self.lblAd.place(x=0, y=0)

        self.btnRight = tk.Button(self, text=">>>", command=lambda: controller.show_frame(TimeTable), height=10)
        self.btnRight.pack(side="right")




print("[ALERT] Client Started")
display = SecondYearProjectClient()
display.master.mainloop()