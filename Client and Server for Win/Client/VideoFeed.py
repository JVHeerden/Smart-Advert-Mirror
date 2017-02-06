import socket
import threading
import cv2
from queue import Queue
import io
import PIL
from PIL import Image
from PIL import ImageTk
import time
import numpy
import App_Sockets
# import picamera
# from picamera import PiCamera
# from picamera.array import PiRGBArray

class VideoFeed():

    def __init__(self, type):
        self.feed_type = type
        self.sock = socket.socket()
        self.host = socket.gethostname()
        self.port = 60000
        self.q = Queue()
        self.capture = None
        self.feed = True
        self.ready = False

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
            if self.feed_type == "Sender":
                self.send()
                break
            else:
                self.receive()
                break

    def getReady(self):
        return self.ready

    def send(self):
        stream = io.BytesIO()
        self.capture = cv2.VideoCapture(0)
        # For use on Pi
        '''
        self.capture = PiCamera()
        self.capture.vflip = True
        self.capture.resolution = (384,384)
        self.capture.framerate = 32
        time.sleep(2)
        rawCapture = PiRGBArray(self.capture, size=(384,384))
        '''

        for _ in range(5):
            time.sleep(0.2)
            temp, frame = self.capture.read()
        self.sock.connect((self.host, self.port))
        print('[Alert] Got connection from server - Starting Video Feed')
        self.ready = True
        '''
        while self.feed:
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                    img = frame.array
                    rawCapture.truncate(0)
        '''
        while self.feed:
            temp, frame = self.capture.read()
            stream = io.BytesIO(frame)
            # stream = io.BytesIO(img)
            l = stream.read(4096)
            while l:
                try:
                    self.sock.send(l)
                except Exception as e:
                    pass
                l = stream.read(4096)
            msg = "Done"
            try:
                self.sock.send(str.encode(msg))
            except Exception as e:
                    pass
            stream.seek(0)
            stream.truncate()
        stream.close()
        self.sock.close()

    def receive(self):
        self.sock.bind((self.host, self.port))           # Bind to the port
        self.sock.listen(5)                              # Now wait for Client Connection.
        stream = io.BytesIO()
        conn, addr = self.sock.accept()         # Establish connection with Client.
        while True:
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
            try:
                image_data = stream.getvalue()
                image_recv = Image.frombytes('RGB', (640, 480), image_data)
                img_cv = numpy.array(image_recv)
            except Exception as e:
                print(e)
                pass

            self.capture = img_cv
            cv2.imshow("sending", img_cv)
            cv2.waitKey(1)
            stream.seek(0)
            stream.truncate()

    def kill(self):
        print("Killing")
        self.feed = False
        print("Feed Status: ", self.feed)
        try:
            self.sock.close()
            print("Socket Closed")
        except Exception as e:
            print(e)
        self.capture.release()
        #cv2.destroyAllWindows()
        self.q.task_done()
        App_Sockets.SendMessage(20002, 'Kill')
        self.q.join()


    def getCapture(self):
        return self.capture