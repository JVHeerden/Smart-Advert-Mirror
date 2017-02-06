import os
import io
import socket
import threading
import numpy
import cv2
import imutils
import glob
import time
import tkinter as tk
from tkinter import ttk
import PIL
from PIL import Image
from PIL import ImageTk
import tkinter as tki
import App_Sockets
import FaceRecognition as fr
import Face
import FeatureMatching
import Vision
from queue import Queue
import datetime

path = os.getcwd()
LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Verdana", 10)
SMALL_FONT = ("Verdana", 8)
#Loads Haarcascades
face_cascade = cv2.CascadeClassifier(path +'/haarcascade/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(path + '/haarcascade/haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(path + '/haarcascade/haarcascade_smile.xml')


class SecondYearProjectServer(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self, "Server")
        tk.Tk.geometry(self, "{0}x{1}+0+0".format(1360, 768))

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="black")
        lblTitle = ttk.Label(self, text="Start Page", font=LARGE_FONT)
        lblTitle.pack(pady=10, padx=10)
        self.controller = controller
        self.btnStart = ttk.Button(self, text="Start", command=lambda: self.more(controller))
        self.btnStart.pack()
        self.btnExit = None

        self.lblDebug = None
        self.lblVideoFeed = None                 # Label in which the video feed is shown
        self.lblPicOne = None                    # Label in which image 1 is shown
        self.lblPicTwo = None                    # Label in which image 2 is shown
        self.lblPicThree = None                  # Label in which image 3 is shown
        self.lblVisionPic = None                 # Label in which image sent to Vision API is shown
        self.capture_lock = threading.Lock()
        self.isRegistered = False
        self.Main_Thread = threading.Thread(target=self.main_program)
        self.frame = None

        stats_file = open((path+"/stats.txt"), 'r')
        stats_data = stats_file.read().split(';')
        stats_file.close()
        self.unique_users = stats_data[0]
        self.new_users = stats_data[1].split(',')
        self.visits = stats_data[2].split(',')
        self.success_rate = stats_data[3]
        print(stats_data[4])
        temp = stats_data[4].replace('-', '', 2)
        print(temp)
        self.the_date = datetime.date(int(temp[0:4]), int(temp[4:6]), int(temp[6:8]))
        self.get_stats_ready()

        #vars
        self.emotion = "None"
        self.user_type = None
        self.user = None
        self.result = "Undetermined"
        self.feed = True
        # Video Feed Information
        self.feed_type = "Receiver"
        self.sock = socket.socket()
        self.host = socket.gethostname()
        self.port = 60000
        self.q = Queue()

    def more(self, controller):
        self.btnStart.destroy()
        #self.btnLeft = tk.Button(self, text="Back", command=lambda: controller.show_frame(TimeTable), height=10)
        #self.btnLeft.pack(side="left")

        self.lbDebug = tk.Listbox(controller, width=48, height=22, bg="black", fg="white")
        self.lbDebug.place(x=0, y=384)
        self.lbDebug.insert(tk.END, "===Debug Window=======================")

        self.emotion = "None"
        self.user_type = None
        self.user = None
        self.result = "Undetermined"
        self.frame = None

        image = cv2.imread('black.jpg')
        image = imutils.resize(image, width=384, height=384)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.lblVideoFeed is None:
            self.lblVideoFeed = tki.Label(controller, width=384, height=384, image=image)
            self.lblVideoFeed.image = image
            self.lblVideoFeed.pack()
            self.lblVideoFeed.place(x=0, y=0)
        else:
            self.lblVideoFeed.configure(image=image)
            self.lblVideoFeed.image = image
        self.Main_Thread = threading.Thread(target=self.main_program)
        self.feedStarter()

    def get_stats_ready(self):
        self.unique_users = int(self.unique_users)
        self.success_rate = float(self.success_rate)

        for i, j in enumerate(self.visits):
            self.visits[i] = int(j)

        for i, j in enumerate(self.new_users):
            self.new_users[i] = int(j)

        last_date = datetime.datetime.today()
        if self.the_date.year > last_date.year:
            # self.new_users[3] += self.new_users[2]
            self.new_users[2] = 0
            self.new_users[1] = 0
            self.new_users[0] = 0
            # self.visits[3] += self.visits[2]
            self.visits[2] = 0
            self.visits[1] = 0
            self.visits[0] = 0

        if self.the_date.month > last_date.month:
            self.new_users[1] = 0
            self.new_users[0] = 0
            self.visits[1] = 0
            self.visits[0] = 0

        if self.the_date.day > last_date.day:
            self.new_users[0] = 0
            self.visits[0] = 0



    def update_stats(self, email):
        self.visits[3] += 1
        self.visits[2] += 1
        self.visits[1] += 1
        self.visits[0] += 1

        if email != 'None' and self.user_type == 'new':
            self.unique_users += 1
            self.new_users[0] += 1
            self.new_users[1] += 1
            self.new_users[2] += 1
            self.new_users[3] += 1

            self.success_rate = self.new_users[3] / self.visits[3] * 100

        stats_file = open((path+"/stats.txt"), 'w')
        stats_file.write((str(self.unique_users) + ";"))
        stats_file.write("{0},{1},{2},{3};".format(self.new_users[0], self.new_users[1], self.new_users[2], self.new_users[3]))
        stats_file.write("{0},{1},{2},{3};".format(self.visits[0], self.visits[1], self.visits[2], self.visits[3]))
        stats_file.write(str(self.success_rate) + ';')
        stats_file.write(datetime.datetime.today().date().__str__())
        stats_file.close()

    def main_program(self):
        response = App_Sockets.ReceiveMessage(20000)
        print("Meh")
        count = 0
        looped = 0
        photos = []
        face_found = False

        while looped < 11:
            time.sleep(0.2)
            if fr.look_for_face(self.frame):
                    count += 1
            if count >= 4:
                face_found = True
                break
            looped += 1

        if face_found:
            App_Sockets.SendMessage(20001, 'Positive')
            count = 0
            looped = 0

            while True:
                temp = self.frame
                temp = fr.take_photo(temp)
                try:
                    if temp != ():
                        photos.append(temp)
                        count += 1
                        print(count)
                except Exception:
                    pass
                if count >= 3:
                    break

            matcher = FeatureMatching.FeatureMatching(photos)
            self.lbDebug.insert(tk.END, "[INFO] Starting Feature Matching")
            print("Starting Feature Matching")
            matcher.startMatching()

            self.user = Face.Face()

            if matcher.isRegistered:
                self.lbDebug.insert(tk.END, "[INFO] Match Found, Matches: ", matcher.matches)
                self.lbDebug.insert(tk.END, "[INFO] Loading Face Object")
                self.result = "Welcome Back!"
                print("Returned User")
                self.user.Existing_Face(matcher.matchedDir)
            else:
                self.lbDebug.insert(tk.END, "[INFO] New User, No Matches Found")
                self.lbDebug.insert(tk.END, "[INFO] Creating Face Object")
                self.result = "New User"
                self.user_type = 'new'
                self.user.New_Face(photos)

            self.LoadPics()
            self.lbDebug.insert(tk.END, "[INFO] Sending user result to client")
            print("Sending user result")
            App_Sockets.SendMessage(20001, self.result)
            #self.CallVision()
            #self.LoadPics()
            print("Sending Emotion Result")
            self.lbDebug.insert(tk.END, "[INFO] Sending emotion result to client")
            App_Sockets.SendMessage(20001, self.emotion)

            if self.result == 'New User':
                email = App_Sockets.ReceiveMessage(20001)
                if email == 'None':
                    print("Not saving user")
                    self.user.Email = email
                else:
                    self.lbDebug.insert(tk.END, "[INFO] Saving User")
                    print("Saving User")
                    print(email)
                    self.user.Email = email
                    self.user.saveFace()

            self.update_stats(self.user.Email)

            App_Sockets.ReceiveMessage(20002)
            self.kill()
        else:
            App_Sockets.SendMessage(20001, 'Negative')
            App_Sockets.ReceiveMessage(20002)
            self.kill()

    def feedStarter(self):
        self.q = Queue()
        t = threading.Thread(target=self.threader)
        # t.daemon = True
        t.start()
        self.q.put(1)
        # self.q.join()

    def threader(self):
        while True:
            self.q.get()

            self.receive()
            break

    def receive(self):
        self.feed = True
        self.sock = socket.socket()
        self.sock.bind((self.host, self.port))           # Bind to the port
        self.sock.listen(5)                              # Now wait for Client Connection.
        stream = io.BytesIO()
        print("Whooooooooooooooooo")
        conn, addr = self.sock.accept()         # Establish connection with Client.
        count = 1
        while self.feed:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                try:
                    temp = data.decode('utf-8')
                    if temp == 'Done':
                        break
                except Exception:
                    pass
                # write data to a stream
                stream.write(data)

            img_cv = None
            try:
                image_data = stream.getvalue()
                image_recv = Image.frombytes('RGB', (640, 480), image_data)
                img_cv = numpy.array(image_recv)
                temp = numpy.array(image_recv)
            except Exception as e:
                print(e)
                pass

            with self.capture_lock:
                self.frame = temp

            self.FeedDisplay(img_cv)
            if count == 1:
                self.Main_Thread.start()
                count += 1
            stream.seek(0)
            stream.truncate()

    def kill(self):
        self.result = "Undetermined"
        self.feed = False
        print("Killing")
        cv2.destroyAllWindows()
        self.sock.close()
        image = cv2.imread('black.jpg')
        image = imutils.resize(image, width=384, height=384)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        self.lblVideoFeed.configure(image=image)
        self.lblVideoFeed.image = image

        image = cv2.imread('black.jpg')
        image = imutils.resize(image, width=384, height=384)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.lblPicOne is None:
            self.lblPicOne = tki.Label(self, width=244, height=192, image=image)
            self.lblPicOne.image = image
            self.lblPicOne.place(x=384, y=0)
        else:
            self.lblPicOne.configure(image=image)
            self.lblPicOne.image = image

        if self.lblPicTwo is None:
            self.lblPicTwo = tki.Label(self, width=244, height=192, image=image)
            self.lblPicTwo.image = image
            self.lblPicTwo.place(x=628, y=0)
        else:
            self.lblPicTwo.configure(image=image)
            self.lblPicTwo.image = image

        if self.lblPicThree is None:
            self.lblPicThree = tki.Label(self, width=244, height=192, image=image)
            self.lblPicThree.image = image
            self.lblPicThree.place(x=384, y=192)
        else:
            self.lblPicThree.configure(image=image)
            self.lblPicThree.image = image

        if self.lblVisionPic is None:
            self.lblVisionPic = tki.Label(self, width=244, height=192, image=image)
            self.lblVisionPic.image = image
            self.lblVisionPic.place(x=384, y=192)
        else:
            self.lblVisionPic.configure(image=image)
            self.lblVisionPic.image = image

        self.q.task_done()
        self.q.join()

        time.sleep(2)
        self.more(self.controller)

    def FeedDisplay(self, img):
        font = cv2.FONT_HERSHEY_SIMPLEX
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 12, 5)
        for (x, y, w, h) in faces[0:1]:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(img, 'Face', (x, y), font, 1, (255, 0, 0), 2, cv2.LINE_AA)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img[y:y+h, x:x+w]
            nh = int(h/2)
            roi_gray_eyes = gray[y:y+nh, x:x+w]

            eyes = eye_cascade.detectMultiScale(roi_gray_eyes)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                cv2.putText(img, 'Eye', (x+ex-5, y+ey-5), font, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            smiles = smile_cascade.detectMultiScale(roi_gray, 3, 30)
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 0, 255), 2)
                cv2.putText(img, 'Smile', (x+sx-5, y+sy-5), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

            cv2.putText(img, self.result, (50, 50), font, 1, (255, 255, 255), 3, cv2.LINE_AA)

        image = imutils.resize(img, width=384, height=384)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = PIL.Image.fromarray(image)
        image = ImageTk.PhotoImage(image)

        if self.lblVideoFeed is None:
            self.lblVideoFeed = tki.Label(self, width=384, height=384, image=image)
            self.lblVideoFeed.image = image
            self.lblVideoFeed.pack()
            self.lblVideoFeed.place(x=0, y=0)
        else:
            self.lblVideoFeed.configure(image=image)
            self.lblVideoFeed.image = image

    def onClose(self):
        self.kill()

    def LoadPics(self):
        images = []
        for i in self.user.photos:
            image = imutils.resize(i, width=244, height=192)
            image = PIL.Image.fromarray(image)
            images.append(ImageTk.PhotoImage(image))

        print(images[0])
        print(images[1])
        print(images[2])
        if self.lblPicOne is None:
            self.lblPicOne = tki.Label(self, width=244, height=192, image=images[0])
            self.lblPicOne.image = images[0]
            self.lblPicOne.place(x=384, y=0)
        else:
            self.lblPicOne.configure(image=images[0])
            self.lblPicOne.image = images[0]

        if self.lblPicTwo is None:
            self.lblPicTwo = tki.Label(self, width=244, height=192, image=images[1])
            self.lblPicTwo.image = images[1]
            self.lblPicTwo.place(x=628, y=0)
        else:
            self.lblPicTwo.configure(image=images[1])
            self.lblPicTwo.image = images[1]

        if self.lblPicThree is None:
            self.lblPicThree = tki.Label(self, width=244, height=192, image=images[2])
            self.lblPicThree.image = images[2]
            self.lblPicThree.place(x=384, y=192)
        else:
            self.lblPicThree.configure(image=images[2])
            self.lblPicThree.image = images[2]
        '''
        image = imutils.resize(self.user.vision, width=244, height=192)
        image = PIL.Image.fromarray(image)
        images.append(ImageTk.PhotoImage(image))

        if self.lblVisionPic is None:
            self.lblVisionPic = tki.Label(self.top_frame, width=244, height=192, image=image)
            self.lblVisionPic.image = image
            self.lblVisionPic.pack()
            self.lblVisionPic.place(x=628, y=192)
        '''

    def CallVision(self):
        self.lbDebug.insert(tk.END, "[ALERT]Calling Vision API")
        visionPath = self.user.filePath + "/vision.png"
        cv2.imwrite(visionPath, self.frame)

        self.user.vision = cv2.imread(visionPath)

        visionResult = Vision.main(visionPath, visionPath, 1)
        person_details = [visionResult[0]['angerLikelihood'], visionResult[0]['surpriseLikelihood'], visionResult[0]['sorrowLikelihood'], visionResult[0]['joyLikelihood']]
        self.lbDebug.insert(tk.END, "===============================================")
        self.lbDebug.insert(tk.END, "===============================================")
        self.lbDebug.insert(tk.END, "Anger Likelihood: " + person_details[0])
        self.lbDebug.insert(tk.END, "Surprised Likelihood: " + person_details[1])
        self.lbDebug.insert(tk.END, "Sorrow Likelihood: " + person_details[2])
        self.lbDebug.insert(tk.END, "Joy Likelihood: " + person_details[3])
        self.lbDebug.insert(tk.END, "===============================================")

        self.lbDebug.insert(tk.END, "[INFO] Determining Ad")
        flag = False
        self.lbDebug.insert(tk.END, "[INFO] Determining Ad")
        if person_details[0] != 'VERY_UNLIKELY':
            self.most_likely = "ANGER"
            flag = True
        if person_details[1] != 'VERY_UNLIKELY':
            self.most_likely = "SURPRISE"
            flag = True
        if person_details[2] != 'VERY_UNLIKELY':
            self.most_likely = "SORROW"
            flag = True
        if person_details[3] != 'VERY_UNLIKELY':
            self.most_likely = "JOY"
            flag = True
        flag = False
        if flag == False:
            self.most_likely = "None"

        self.lbDebug.insert(tk.END, "===============================================")
        self.lbDebug.insert(tk.END, "[INFO] Most Likely Emotion: " + self.most_likely)
        self.lbDebug.insert(tk.END, "===============================================")


print("[ALERT] Server Started")
display = SecondYearProjectServer()
display.mainloop()