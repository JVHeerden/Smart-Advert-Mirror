import socket
import threading
import cv2
from Queue import Queue
import io
import PIL
from PIL import Image
from PIL import ImageTk
import time
import numpy
import App_Sockets
import picamera
from picamera import PiCamera
#from picamera.array import PiRGBArray
import struct

class VideoFeed():

    pi_cam = None
    def __init__(self, type):
        self.feed_type = type
        self.sock = socket.socket()
        #self.host = socket.gethostname()
        self.host = "DESKTOP-AK7MCHR"
        print(self.host)
        self.port = 60000
        self.q = Queue()
        self.capture = None
        self.feed = True
        self.ready = False

    def feedStarter(self):
        try:
            VideoFeed.pi_cam = picamera.PiCamera()
        except Exception:
            pass
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
        #self.sock.connect(('192.168.1.104', 60000))
        self.sock.connect(('169.254.61.173', 60000))
        connection = self.sock.makefile('wb')
    
        try:
            with VideoFeed.pi_cam as camera:
                camera.vflip = True
                camera.resolution = (384,384)
                cameraframerate = 32
                #camera.start_preview()
                time.sleep(2)

                stream = io.BytesIO()
                self.Feed = True
                while self.Feed:
                    for frame in camera.capture_continuous(stream, 'bgr', use_video_port = True):
                        connection.write(struct.pack('<L', stream.tell()))
                        connection.flush()
                        stream.seek(0)
                        connection.write(stream.read())

                        stream.seek(0)
                        stream.truncate()
                connection.write(struct.pack('<L', 0))
        finally:
            connection.close()
            self.sock.close()
            VideoFeed.pi_cam.close()

    '''    
    def send(self):
        stream = io.BytesIO()
        #self.capture = cv2.VideoCapture(0)
        # For use on Pi
        
        camera = PiCamera()
        camera.vflip = True
        camera.resolution = (384,384)
        cameraframerate = 32
        time.sleep(2)
        rawCapture = PiRGBArray(camera, size=(384,384))
        
    '''
    '''
        for _ in range(5):
            time.sleep(0.2)
            temp, frame = self.capture.read()
    '''
    '''
        self.sock.connect(('192.168.1.104', 60000))
        #self.sock.connect((self.host, self.port))
        print('[Alert] Got connection from server - Starting Video Feed')
        self.ready = True
        self.Feed = True
        while self.Feed:
    '''
    '''
            print('yeah')
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                #img = frame
                rawCapture.truncate(0)
                print('wtf')
                    

                # stream = io.BytesIO(frame)
                stream = io.BytesIO(img)
                print(stream)
                l = stream.read(4096)
                while l:
                    try:
                        self.sock.send(l)
                    except Exception as e:
                        pass
                    l = stream.read(4096)
                msg = "Done"
                print('Frame Done')
                try:
                    self.sock.send(str.encode(msg))
                except Exception as e:
                    print(e)
                    pass
                stream.seek(0)
                stream.truncate()
    '''
    '''
        stream.close()
        self.sock.close()
    '''
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
        try:
            VideoFeed.pi_cam.close()
        except Exception:
            pass
        print("Feed Status: ", self.feed)
        try:
            self.sock.close()
            print("Socket Closed")
        except Exception as e:
            print(e)
        #self.capture.release()
        #cv2.destroyAllWindows()
        self.q.task_done()
        App_Sockets.SendMessage(20002, 'Kill')
        self.q.join()


    def getCapture(self):
        return self.capture
