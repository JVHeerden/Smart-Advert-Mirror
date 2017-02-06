import cv2
import os

path = os.getcwd()


def look_for_face(temp_img_img):
    try:
        print("Looking for face")
        face_cascade = cv2.CascadeClassifier(path +'/haarcascade/haarcascade_frontalface_default.xml')
        g = cv2.cvtColor(temp_img_img, cv2.COLOR_BGR2GRAY)
        detection = face_cascade.detectMultiScale(g, 8, 5)
        print("Detection: ", detection)
        if detection == ():
            return False
        else:
            return True
    except Exception as e:
        print(e)
        return False


def take_photo(temp_img):
    print("Taking Photo")
    face_cascade = cv2.CascadeClassifier(path +'/haarcascade/haarcascade_frontalface_default.xml')
    g = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
    detection = face_cascade.detectMultiScale(g, 8, 5)
    print("Detection: ", detection)
    if detection == ():
        return detection
    else:
        for (x, y, w, h) in detection[0:1]:
            roi_gray = g[y:y+h+20, x:x+w+20]
        return roi_gray
