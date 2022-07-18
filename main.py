import base64

import cv2
import numpy as np
import face_recognition
import os
import requests
from tkinter import messagebox, Tk, Label
import tkinter as tk
import json
from PIL import Image, ImageTk
from time import strftime
import time
from datetime import date
from playsound import playsound
import io
import base64
from threading import Thread
import httpx

# *************** Configs *******************
SOURCE = 2
TOLERANCE = 0.50
CLEAN_UP_DELAY = 10

# ************** Face Recognition ***************

API_LINK = "http://localhost/skooltechpro_web/api"
#API_LINK = "https://skooltech.com/pro/api"
# SHHS
# SCHOOL_ID = "2NWhWyxbmx"
# path = 'shhs_training_images'

# CCPSI
#SCHOOL_ID = "ivvzCkiUC1"
#path = 'ccpsi_training_images'

#SkoolTech
SCHOOL_ID = "LeBDKSw1rP"
path = "skooltech_training_images"

images = []
classNames = []
myList = os.listdir(path)
color = "#000080"

detected = []
detectedList = []
cleanFlag = False
startTime = 0

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


encodeListKnown = findEncodings(images)

# cap = cv2.VideoCapture(2)

months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
updateDateFlag = False

window = tk.Tk()
window.title("SkoolTech Pro")
window.geometry("1360x720")
window.configure(bg="white")
window.resizable(False, False)
window.update()
window.attributes("-fullscreen", True)
windowWidth = window.winfo_width()
windowHeight = window.winfo_height()

headerFrame = tk.Frame(window, width=windowWidth, height=80, bg="#000080")
headerFrame.grid(row=0, column=0, columnspan=6)
timeLabel = Label(headerFrame, font=("calibri light", 35), fg="white", text="88:88 AM")
timeLabel.place(x=windowWidth - 230, y=25)
dateLabel = Label(headerFrame, font=("calibri light", 18), fg="white", text="FEB 9, 1986")
dateLabel.place(x=windowWidth - 180, y=0)

footerFrame = tk.Frame(window, width=windowWidth, height=30, bg="#000080")
footerFrame.grid(row=3, column=0, columnspan=6)
footerFrame.pack_propagate(False)

footerLabel = tk.Label(footerFrame, text="POWERED BY SKOOLTECH SOLUTIONS", fg="white")
footerLabel.pack(pady=5)

schoolNameLabel = Label(headerFrame, font=("calibri light", 25), fg="white", text="88:88 AM")
schoolNameLabel.place(x=85, y=10)
schoolAddressLabel = Label(headerFrame, font=("calibri light", 12), fg="white", text="FEB 9, 1986")
schoolAddressLabel.place(x=85, y=45)

frameWidth = (windowWidth / 6) - 10
frameHeight = (windowHeight / 2) - 65
framePadY = 5
framePadX = 5

frame1 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame1.grid(row=1, column=0, pady=framePadY, padx=framePadX)

frame2 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame2.grid(row=1, column=1, pady=framePadY, padx=framePadX)

frame3 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame3.grid(row=1, column=2, pady=framePadY, padx=framePadX)

frame4 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame4.grid(row=1, column=3, pady=framePadY, padx=framePadX)

frame5 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame5.grid(row=1, column=4, pady=framePadY, padx=framePadX)

frame6 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame6.grid(row=1, column=5, pady=framePadY, padx=framePadX)

frame7 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame7.grid(row=2, column=0, pady=framePadY, padx=framePadX)

frame8 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame8.grid(row=2, column=1, pady=framePadY, padx=framePadX)

frame9 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame9.grid(row=2, column=2, pady=framePadY, padx=framePadX)

frame10 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame10.grid(row=2, column=3, pady=framePadY, padx=framePadX)

frame11 = tk.Frame(window, width=(frameWidth * 2) + 10, height=frameHeight, bg="#FFFFFF")
frame11.grid(row=2, column=4, pady=framePadY, padx=framePadX, columnspan=2)
frame11.pack_propagate(False)

videoLabel = tk.Label(frame11, width=int(frameWidth * 2), height=int(frameHeight) - 10, bg="#000080")
videoLabel.pack(pady=5)


def updateDate():
    global updateDateFlag
    updateDateFlag = True
    today = date.today()
    year = today.year
    month = months[today.month]
    day = today.day
    dateString = month + " " + str(day) + "," + str(year)
    dateLabel.configure(text=dateString)


def updateTime():
    global updateDateFlag
    string = strftime("%H:%M:%S")
    timeLabel.config(text=string)
    timeLabel.after(1000, updateTime)
    if string == "00:00:01" and not updateDateFlag:
        updateDate()
    if string == "01:00:00" and updateDateFlag:
        updateDateFlag = False


def showMessage(message, type='info', timeout=1000):
    try:
        root = Tk()
        root.withdraw()
        root.after(timeout, root.destroy)
        if type == 'info':
            messagebox.showinfo('Info', message, master=root)
        elif type == 'warning':
            messagebox.showwarning('Warning', message, master=root)
        elif type == 'error':
            messagebox.showerror('Error', message, master=root)
    except:
        pass


def getSchoolDetail():
    url = API_LINK + "/school.php"
    data = {'id': SCHOOL_ID}
    r = requests.post(url, data=data)
    response = r.text
    resp = response.split("*_*")
    if len(resp) > 0:
        if resp[0] == "true":
            renderSchoolDetail(resp[1])
        elif resp[0] == "false":
            showMessage(resp[1], "warning")
        else:
            showMessage(response, "error")


def renderSchoolDetail(data):
    global color
    details = json.loads(data)
    base64Image = details[0]["image"].split(",")
    image = base64Image[1]
    name = details[0]["name"]
    address = details[0]["address"]
    color = details[0]["color"]

    headerFrame.configure(bg=color)
    timeLabel.configure(bg=color)
    dateLabel.configure(bg=color)
    schoolNameLabel.configure(bg=color)
    schoolAddressLabel.configure(bg=color)
    footerLabel.configure(bg=color)
    footerFrame.configure(bg=color)
    frame11.configure(bg=color)

    schoolNameLabel.configure(text=name)
    schoolAddressLabel.configure(text=address)

    # Create logo label container
    img = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))
    resized_image = img.resize((70, 70))

    logo = ImageTk.PhotoImage(resized_image)
    label = Label(headerFrame, image=logo)
    label.place(x=5, y=5)
    label.image = logo


def cleanDetected():
    global detected
    detected = []


def setCleanSchedule():
    global cleanFlag, startTime
    if not cleanFlag:
        startTime = time.time() + CLEAN_UP_DELAY
        cleanFlag = True


def playBeep():
    playsound("beep.wav", block=False)


def markAttendance(_id):
    url = API_LINK + "/attendance.php"
    data = {'schoolid': SCHOOL_ID, 'studentid': _id}
    r = httpx.post(url, data=data)
    response = r.text
    resp = response.split("*_*")
    if len(resp) > 0:
        if resp[0] == "true":
            renderStudentDetail(resp[1])
        elif resp[0] == "false":
            showMessage(resp[1], "warning")
        else:
            showMessage(response, "error")


def renderStudentDetail(data):
    details = json.loads(data)
    base64Image = details[0]["image"].split(",")
    image = base64Image[1]
    name = details[0]["name"]
    _type = details[0]["type"]
    grade = details[0]["grade"]
    section = details[0]["section"]
    activity = details[0]["activity"]
    if activity == "login":
        activity = "Logged Out"
    else:
        activity = "Logged In"
    if len(detectedList) > 9:
        detectedList.pop(0)
    student = [image, name, _type, grade, section, activity]
    detectedList.append(student)
    renderDetected(detectedList)


def renderDetected(data):
    global color
    i = 0
    for _list in reversed(data):
        _image = _list[0]
        name = _list[1]
        _type = _list[2]
        activity = _list[5]

        if i > 5:
            studentFrame = tk.Frame(window, width=frameWidth, height=frameHeight, bg=color)
            studentFrame.grid(row=2, column=i - 6, pady=framePadY, padx=framePadX)
        else:
            studentFrame = tk.Frame(window, width=frameWidth, height=frameHeight, bg=color)
            studentFrame.grid(row=1, column=i, pady=framePadY, padx=framePadX)

        i += 1

        _img = Image.open(io.BytesIO(base64.decodebytes(bytes(_image, "utf-8"))))
        imageWidth = int(frameWidth - 12)
        resized_image = _img.resize((imageWidth, imageWidth))
        studentImage = ImageTk.PhotoImage(resized_image)
        studentImageLabel = tk.Label(studentFrame, image=studentImage)
        studentImageLabel.place(x=5, y=5)
        studentImageLabel.image = studentImage
        # studentName = tk.Label(studentFrame, anchor="center", text=name, width=22)
        studentName = tk.Label(studentFrame, anchor="center", text=name, width=25)
        studentName.place(x=5, y=imageWidth + 10)
        # studentDetails = tk.Label(studentFrame, anchor="center", text=_type + " - " + activity, width=22, fg="white", bg=color)
        studentDetails = tk.Label(studentFrame, anchor="center", text=_type + " - " + activity, width=25, fg="white",
                                  bg=color)
        studentDetails.place(x=5, y=imageWidth + 32)


getSchoolDetail()
updateTime()
updateDate()


class VideoGet(tk.Tk):
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()

    def stop(self):
        self.stopped = True


video_getter = VideoGet(SOURCE).start()

while True:
    if cleanFlag:
        if time.time() > startTime:
            cleanFlag = False
            cleanDetected()

    if video_getter.stopped:
        video_getter.stop()
        break

    img = video_getter.frame
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace, TOLERANCE)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            studentId = classNames[matchIndex].upper()

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            if studentId not in detected:
                t1 = Thread(target=playBeep())
                t1.start()
                setCleanSchedule()
                detected.append(studentId)
                t2 = Thread(target=markAttendance(studentId))
                t2.start()

    image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    videoLabel.configure(image=image)
    window.update_idletasks()
    window.update()
