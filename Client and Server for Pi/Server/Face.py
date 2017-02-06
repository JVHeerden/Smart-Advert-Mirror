import os
import glob
import cv2
import datetime


class Face():

    def __init__(self):
        self.createdOn = ""
        self.filePath = ""
        self.photos = []
        self.vision = []
        self.statsFile = ""
        self.Email = None
        self.visits = 0

    # Builds a new face
    def New_Face(self, photos):
        # Example: YYYY-MM-DD-hh-mm-ss
        self.createdOn = str(datetime.datetime.now().date()) + "-" + str(datetime.datetime.now().hour) + "-" + str(datetime.datetime.now().minute) + "-" + str(datetime.datetime.now().second)
        # Example: C:\path\faces_captured\YYYY-MM-DD-hh-mm-ss
        self.filePath = os.getcwd() + "/faces_captured/" + self.createdOn
        # Photos (3) taken when doing Feature Matching
        self.photos = photos
        # Will contain Photo to be send to the Vision API
        self.vision = []
        # Contains the path the Info File will be saved to
        # CreatedOn, Visits
        self.statsFile = self.filePath + "/info.txt"
        self.Email = None

    # Builds an existing face

    def Existing_Face(self, path):
        # Example: YYYY-MM-DD-hh-mm-ss
        self.createdOn = path[len(path)-19:]
        # Example: C:\path\faces_captured\YYYY-MM-DD-hh-mm-ss
        self.filePath = path
        # Photos (3) loaded from face directory
        self.photos = self.loadPhotos()
        # Will contain Photo to be send to the Vision API
        self.vision = []
        # Contains the path the Info File will be saved to
        self.statsFile = self.filePath + "/info.txt"
        self.load_info()

    # Loads photos out of existing directory
    def loadPhotos(self):
        photoDirs = glob.glob(self.filePath + "/*.jpg")
        photos = []
        for i in photoDirs:
            photos.append(cv2.imread(i))
        return photos

    def load_info(self):
        file = open(self.statsFile, "r")
        text = file.read()
        file.close()
        info = text.split(',')
        print(info)
        self.Email = info[2]
        self.visits = int(info[1]) + 1
        file = open(self.statsFile, "w")
        file.write(self.createdOn + ',')
        file.write(str(self.visits) + ',')
        file.write(self.Email)
        file.close()
        print("This is the users' email!", self.Email)

    # Saves the new user
    def saveFace(self):
        os.mkdir(self.filePath)
        file = open(self.statsFile, "w")
        file.write(self.createdOn + ",1")
        file.write("," + self.Email)
        file.close()
        for i in range(3):
            path = self.filePath + "/" + str(i) + ".jpg"
            cv2.imwrite(path, self.photos[i])

