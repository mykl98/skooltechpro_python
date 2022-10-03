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

# *************** Configs *******************
SOURCE = 0
TOLERANCE = 0.50
CLEAN_UP_DELAY = 10

# ************** School and API Configs ***************
API_LINK = "https://skooltech.com/pro/api"

SCHOOL_ID = "LeBDKSw1rP"
path = '/home/mykl/skooltechpro_python/training_images'
# ***************** Variables ****************
myList = os.listdir(path)
images = []
classNames = []
encodeListKnown = []
detected = []
detectedList = []
color = "#000080"
cleanFlag = False
startTime = 0
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
updateDateFlag = False
callApiFlag = False
callApiThread = None
messageRoot = None


# **************** Thread Class ***************
class CallApi(Thread):
    def __init__(self, callApiUrl, callApiData, callApiType):
        super().__init__()
        self.url = callApiUrl
        self.data = callApiData
        self.type = callApiType
        self.response = None
        self.error = None

    def run(self) -> None:
        try:
            r = requests.post(self.url, data=self.data)
            self.response = r.text
        except requests.exceptions.Timeout:
            self.error = "API call timed out!"
        except requests.exceptions.TooManyRedirects:
            self.error = "Bad URL request, too many redirects!"
        except requests.exceptions.RequestException as e:
            self.error = "Catastrophic error: " + str(e)


window = tk.Tk()
window.title("SkoolTech Pro")
window.geometry("1360x720")
window.configure(bg="white")
window.resizable(False, False)
window.attributes("-fullscreen", True)
window.update()
windowWidth = window.winfo_width()
windowHeight = window.winfo_height()
window.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="column")

headerFrame = tk.Frame(window, width=windowWidth, height=80, bg="#000080")
headerFrame.grid(row=0, column=0, columnspan=6)

schoolNameLabel = Label(headerFrame, font=("calibre light", 25), fg="white", bg=color, text="SkoolTech Solution Academy")
schoolNameLabel.place(x=85, y=10)
schoolAddressLabel = Label(headerFrame, font=("calibre light", 12), fg="white", bg=color, text="Block 16 lot 18-19 Belair Subdivision Buru-un Iligan City")
schoolAddressLabel.place(x=85, y=45)

timeLabel = Label(headerFrame, font=("calibre light", 35), fg="white", bg=color, text="88:88 AM")
timeLabel.place(x=windowWidth - 230, y=25)
dateLabel = Label(headerFrame, font=("calibre light", 18), fg="white", bg=color, text="FEB 9, 1986")
dateLabel.place(x=windowWidth - 180, y=0)

footerFrame = tk.Frame(window, width=windowWidth, height=30, bg="#000080")
footerFrame.grid(row=3, column=0, columnspan=6)
footerFrame.pack_propagate(False)

footerLabel = tk.Label(footerFrame, text="POWERED BY SKOOLTECH SOLUTIONS", fg="white", bg=color)
footerLabel.pack(pady=5)

frameWidth = (windowWidth / 6) - 10
frameHeight = (windowHeight / 2) - 65
framePadY = 5
framePadX = 5

frame1 = tk.Frame(window, width=frameWidth, height=frameHeight, bg="#FFFFFF")
frame1.grid(row=1, column=0, pady=framePadY, padx=framePadX)

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
    month = months[today.month-1]
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
    global messageRoot
    try:
        messageRoot = Tk()
        messageRoot.withdraw()
        if timeout != -1:
            messageRoot.after(timeout, messageRoot.destroy)
        if type == 'info':
            messagebox.showinfo('Info', message, master=messageRoot)
        elif type == 'warning':
            messagebox.showwarning('Warning', message, master=messageRoot)
        elif type == 'error':
            messagebox.showerror('Error', message, master=messageRoot)
    except:
        pass


def GetSchoolDetail():
    global callApiFlag, callApiThread
    url = API_LINK + "/school.php"
    data = {'id': SCHOOL_ID}
    thread = CallApi(callApiUrl=url, callApiData=data, callApiType="getSchoolDetail")
    thread.start()
    callApiFlag = True
    callApiThread = thread


def RenderSchoolDetail(data):
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
    window.update()


def cleanDetected():
    global detected
    detected = []


def setCleanSchedule():
    global cleanFlag, startTime
    if not cleanFlag:
        startTime = time.time() + CLEAN_UP_DELAY
        cleanFlag = True


def playBeep():
    playsound("/home/mykl/skooltechpro_python/beep.wav", block=False)


def SendNotification(id):
    url = API_LINK + "/send-notification.php"
    data = {'schoolid': SCHOOL_ID, 'studentid': id}
    thread = CallApi(callApiUrl=url, callApiData=data, callApiType="sendNotification")
    thread.start()


def GetStudentDetail(id):
    global callApiFlag, callApiThread
    url = API_LINK + "/attendance.php"
    data = {'schoolid': SCHOOL_ID, 'studentid': id}
    thread = CallApi(callApiUrl=url, callApiData=data, callApiType="getStudentDetail")
    thread.start()
    callApiFlag = True
    callApiThread = thread


def RenderStudentDetail(data):
    details = json.loads(data)
    base64Image = details[0]["image"].split(",")
    image = base64Image[1]
    #id = details[0]["id"]
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
    RenderDetected(detectedList)
    if _type == "Student":
        id = details[0]["id"]
        SendNotification(id)



def RenderDetected(data):
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
        studentDetails = tk.Label(studentFrame, anchor="center", text=_type + " - " + activity, width=25, fg="white",
                                  bg=color)
        studentDetails.place(x=5, y=imageWidth + 32)


GetSchoolDetail()
updateTime()
updateDate()

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    print(classNames)
    return encodeList


encodeListKnown = findEncodings(images)
cap = cv2.VideoCapture(SOURCE)
while True:
    if callApiFlag:
        if callApiThread.error is not None:
            callApiFlag = False
            error = callApiThread.error
            showMessage(message=error, type="error", timeout=5000)
        if callApiThread.response is not None:
            callApiFlag = False
            response = callApiThread.response
            resp = response.split("*_*")
            if len(resp) > 0:
                if resp[0] == "true":
                    if callApiThread.type == "getStudentDetail":
                        RenderStudentDetail(resp[1])
                    else:
                        RenderSchoolDetail(resp[1])
                elif resp[0] == "false":
                    showMessage(resp[1], "warning")
                else:
                    showMessage(response, "error")

    if cleanFlag:
        if time.time() > startTime:
            cleanFlag = False
            cleanDetected()

    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    img = cv2.resize(img, (0, 0), None, 0.68, 0.68)
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = int(y1 * 2.8), int(x2 * 2.8), int(y2 * 2.8), x1 * 3
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if callApiFlag is False:
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace, TOLERANCE)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                studentId = classNames[matchIndex].upper()

                if studentId not in detected:
                    setCleanSchedule()
                    detected.append(studentId)
                    playBeep()
                    GetStudentDetail(studentId)

    image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    image = Image.fromarray(image)
    image = ImageTk.PhotoImage(image)
    videoLabel.configure(image=image)
    window.update_idletasks()
    window.update()
