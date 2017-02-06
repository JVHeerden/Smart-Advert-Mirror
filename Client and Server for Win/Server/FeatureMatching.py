import os
import glob
import cv2
import threading
from queue import Queue


class FeatureMatching():

    # Creates feature matching object
    def __init__(self, photos):
        path = os.getcwd() + "/faces_captured/*"
        # Directories of all user in the database
        self.directories = glob.glob(path)
        # Photos of the current user
        self.template = photos
        # Number of matches with photos stored in database
        self.matches = 0
        # Whether this is a returning user or not
        self.isRegistered = False
        # The directory in which the user is saved if it is matched
        self.matchedDir = ""
        self.q = None
        self.templateLock = threading.Lock()
        self.matchesLock = threading.Lock()

    def startMatching(self):
        self.q = Queue()
        for i in range(4):
            t = threading.Thread(target=self.threader)
            t.daemon = True
            t.start()

        for worker in self.directories:
            self.q.put(worker)

        self.q.join()

    def threader(self):
        while True:
            worker = self.q.get()
            self.matcher(worker)
            self.q.task_done()

    def matcher(self, dir):
        sift = cv2.xfeatures2d.SIFT_create()
        # All the paths to the photos in a specific dir
        photoPaths = glob.glob((dir + "/*.jpg"))
        # Photos of a specific dir
        tempPhotos = []
        for i in range(3):
            tempPhotos.append(cv2.imread(photoPaths[i]))

        #with self.templateLock:
        templates = self.template
        totalMatches = []

        for i in templates:
            kp1, des1 = sift.detectAndCompute(i, None)
            for k in tempPhotos:
                kp2, des2 = sift.detectAndCompute(k, None)
                bf = cv2.BFMatcher()
                matches = bf.knnMatch(des1, des2, k=2)
                for m, n in matches:
                    if m.distance < 0.4*n.distance:
                        totalMatches.append([m])
            if len(totalMatches) > 2:
                break

        if len(totalMatches) > 2:
            with self.matchesLock:
                self.matches = len(totalMatches)
                self.isRegistered = True
                self.matchedDir = dir

