import cv2
import numpy as np
import face_recognition
import os
import requests
from tkinter import messagebox, Tk, Label
import tkinter as tk
import json


class Person:
    image = ""
    name = ""
    category = ""
    grade = ""
    section = ""


TOLERANCE = 0.54
API_LINK = "http://localhost/skooltechplus_web/api"
SCHOOL_ID = "2NWhWyxbmx"
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)

window = tk.Tk()
window.title = "SkoolTech Solutions"
window.attributes("-fullscreen", True)
window.update()

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
    if (len(resp) > 0):
        if resp[0] == "true":
            renderSchoolDetail(resp[1])
        elif resp[0] == "false":
            showMessage(resp[1], "warning")
        else:
            showMessage(response, "error")


def renderSchoolDetail(data):
    details = json.loads(data)
    base64 = details[0]["image"].split(",")
    image = base64[1]
    name = details[0]["name"]
    address = details[0]["address"]
    color = details[0]["color"]

    # Create header frame
    headerFrame = tk.Frame(window, width=window.winfo_width(), height=80, bg=color)
    headerFrame.pack(padx=10, pady=10)

    # Create logo frame
    logoFrame = tk.Frame(headerFrame, width=60, height=60)
    logoFrame.pack()

    # Create logo label container
    logo = tk.PhotoImage(data=image)
    label = Label(logoFrame, image=logo)
    label.pack(side="left")
    label.image = logo

def markAttendance(studentId):
    url = API_LINK + "/attendance.php"
    data = {'schoolid': SCHOOL_ID, "studentid": studentId}
    response = requests.post(url, data=data)

encodeListKnown = findEncodings(images)
getSchoolDetail()

cap = cv2.VideoCapture(2)

while True:
    success, img = cap.read()
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
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            markAttendance(studentId)

    #cv2.imshow('Webcam', img)
    cv2.waitKey(1)

    window.mainloop()
