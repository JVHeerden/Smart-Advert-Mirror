import Tkinter as tk
#from Tkinter import ttk
import os
import cv2
import numpy
import imutils
import PIL
from PIL import Image
from PIL import ImageTk
import time
import App_Sockets
import threading
import VideoFeed
import glob
from random import randint
# import RPi.GPIO as GPIO

path = os.getcwd()
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)

class SecondYearProjectClient(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Client")
        tk.Tk.geometry(self, "{0}x{1}+0+0".format(1360, 768))

        tk.Tk.wm_title(self, "Client")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, TimeTable, EventInfo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        lblTitle = tk.Label(self, text="Ad Page", font=LARGE_FONT)
        lblTitle.pack(pady=10, padx=10)
        self.controller = controller
        self.btnStart = tk.Button(self, text="Start", command=lambda: self.showmore(controller))
        self.btnStart.pack()
        self.lblAd = None
        self.btnRight = None
        self.btnLeft = None
        self.isRegistered = False
        self.video_feed = VideoFeed.VideoFeed("Sender")
        self.main_thread = threading.Thread(target=self.main_program)

        self.email = None
        self.lblPopup = None
        self.txtEmail = None
        self.btnOkay = None
        self.btnCancel = None
        self.count = 0

    '''
    def popupmes(self):
        popup = tk.Tk()
        count = 0
        def leavemini():
            self.email = txtEmail.get()
            popup.destroy()

        popup.wm_title("Register?")
        label = tk.Label(popup, text="Do you want to register?", font=NORM_FONT)
        label.pack(side="top", fill="x", pady="10")
        txtEmail = tk.Entry(popup)
        txtEmail.pack()
        B1 = tk.Button(popup, text="Okay", command=leavemini)
        B1.pack(side="left")
        B2 = tk.Button(popup, text="Bye!", command=leavemini)
        B2.pack(side="right")
        while True:
            time.sleep(0.5)
            count += 1
            print(count)
            if count > 60:
                leavemini()
        popup.mainloop()
    '''
    
    def showmore(self, controller):
        self.video_feed = VideoFeed.VideoFeed("Sender")
        self.btnStart.destroy()
        print("Starting Feed Now")
        self.video_feed.feedStarter()
        print('fun')
        print('fun')
        image = cv2.imread('Background.jpg')
        image = imutils.resize(image, width=1360, height=768)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.lblAd is None:
            self.lblAd = tk.Label(self, width=1360, height=768, image=image)
            self.lblAd.image = image
            self.lblAd.place(x=0, y=0)

        self.main_thread = threading.Thread(target=self.main_program)
        self.main_thread.start()

    def leavemini(self):
        self.email = self.txtEmail.get()
        self.count = 61

    def main_program(self):
        inputVar = 0     # This should be deleted when motion sensor is installed, only to emulate motion detection
        # Only for use with Pi
        '''
        GPIO.setmode(GPIO.BOARD)
        pinNr = 7
        GPIO.setup(pinNr, GPIO.IN)
        inputVar = GPIO.input(pinNr)
        '''
        while True:
            # inputVar = GPIO.input(pinNr) #For use with Pi
            if inputVar == 0:
                for _ in range(5):
                    try:
                        print('Sending')
                        App_Sockets.SendMessage(20000, 'Start')
                        break
                    except Exception as e:
                        print(e)
                        pass
                    time.sleep(0.2)
                print("{ALERT} Person Detected")
                break

        #while self.video_feed.getReady() == False:
        #    pass
        self.isRegistered = False
        print("[ALERT] Main Program Started")
        print("[INFO] Waiting for response from server.")
        response = App_Sockets.ReceiveMessage(20001)
        print(response)
        if response == "Positive":
            response = App_Sockets.ReceiveMessage(20001)
            if response == "Welcome Back!":
                self.isRegistered = True

            print(response)
            print("[INFO] Waiting for emotion response from server.")
            response = App_Sockets.ReceiveMessage(20004)
            print(response)
            #server_response = 'None'
            print("[INFO] Determining Ad")
            if response == 'joy':
                ads = glob.glob(path + "/ads/joy/*")
            if response == 'sorrow':
                ads = glob.glob(path + "/ads/sorrow/*")
            if response == 'surprise':
                ads = glob.glob(path + "/ads/surprise/*")
            if response == 'anger':
                ads = glob.glob(path + "/ads/anger/*")
            if response == 'No Emotion':
                ads = glob.glob(path + "/ads/*/*")
            #print(ads)
            selection = randint(1, len(ads)) - 1
            ad = ads[selection]
            print("[INFO] Selected Ad: " + ad)
            print("[ALERT] Starting Ad")

            count = 0
            cap = cv2.VideoCapture(ad)
            print(ad)
            self.email = ''
            while True:
                _, frame = cap.read()
                image = imutils.resize(frame, width=1360, height=768)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = PIL.Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                self.lblAd.configure(image=image)
                self.lblAd.image = image
                count += 1
                print(count)
                if count > 120:
                    break
            
            if self.isRegistered == False:
                image_path = path + "/event_info/register.jpg"
                print(image_path)
                image = cv2.imread(image_path)
                image = imutils.resize(image, width=1360, height=768)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = PIL.Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                self.lblAd = tk.Label(self, width=1360, height=768, image=image)
                self.lblAd.image = image
                self.lblAd.place(x=0, y=0)

                self.count = 0
                self.lblPopup = tk.Label(self, text="Do you want to register?", font=NORM_FONT)
                self.lblPopup.place(x=600, y=360)
                self.txtEmail = tk.Entry(self)
                self.txtEmail.place(x=600, y=380)
                self.btnOkay = tk.Button(self, text="Okay", command=self.leavemini)
                self.btnOkay.place(x=600, y=400)
                self.btnCancel = tk.Button(self, text="Bye!", command=self.leavemini)
                self.btnCancel.place(x=680, y=400)
                while True:
                    time.sleep(0.5)
                    self.count += 1
                    print(self.count)
                    if self.count > 60:
                        self.leavemini()
                        break
                print(self.email)
                self.lblPopup.destroy()
                self.txtEmail.destroy()
                self.btnOkay.destroy()
                self.btnCancel.destroy()
                if self.email is None or self.email == '' or self.email == ' ':
                    App_Sockets.SendMessage(20001, 'None')
                else:
                    App_Sockets.SendMessage(20001, self.email)
                        
            else:
                self.btnLeft = tk.Button(self, text="<<<", command=lambda: self.controller.show_frame(TimeTable), height=10)
                self.btnLeft.pack(side="left")

                self.btnRight = tk.Button(self, text=">>>", command=lambda: self.controller.show_frame(EventInfo), height=10)
                self.btnRight.pack(side="right")
                self.count = 0
                while self.count < 60:
                    time.sleep(0.1)
                    print(self.count)
                    self.count += 1
                self.controller.show_frame(StartPage)


        #self.btnStart = ttk.Button(self, text="Start", command=lambda: self.showmore(self.controller))
        #self.btnStart.pack()
        if self.btnLeft is not None:
            self.btnLeft.destroy()
            self.btnRight.destroy()
        
        image = cv2.imread('Background.jpg')
        image = imutils.resize(image, width=1360, height=768)
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.lblAd.configure(image=image)
        self.lblAd.image = image
        self.video_feed.kill()
        print("Whoop")
        time.sleep(2)
        self.showmore(self.controller)

class TimeTable(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent,  bg="blue")
        lblTitle = tk.Label(self, text="Time Table", font=LARGE_FONT)
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
        lblTitle = tk.Label(self, text="Event Info", font=LARGE_FONT)
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
display.mainloop()
