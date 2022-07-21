import threading

import cv2
import numpy as np
import face_recognition
import os
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
SOURCE = 0
TOLERANCE = 0.50
CLEAN_UP_DELAY = 2

# *************** School and API Configs ******************
API_LINK = "http://localhost/skooltechpro_web/api"
# API_LINK = "https://skooltech.com/pro/api"
# SHHS
# SCHOOL_ID = "2NWhWyxbmx"
# path = '../shhs_training_images'

# CCPSI
SCHOOL_ID = "ivvzCkiUC1"
path = '../ccpsi_training_images'

# SkoolTech
# SCHOOL_ID = "LeBDKSw1rP"
# path = "../skooltech_training_images"

# **************** Variables *******************
images = []
classNames = []
encodeListKnown = []
myList = os.listdir(path)
color = "#000080"
detectedList = []
months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
updateDateFlag = False
initializeFlag = False


class InitFaceRecognition(Thread):
    def __init__(self):
        super().__init__()
        self.knownList = []

    def run(self):
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])

        for _img in images:
            _img = cv2.cvtColor(_img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(_img)[0]
            self.knownList.append(encode)


class ApiCall(Thread):
    def __init__(self, url, data):
        super().__init__()
        self.url = url
        self.data = data
        self.response = None

    def run(self):
        r = httpx.post(self.url, data=self.data)
        self.response = r.text


class ShowMessage(Thread):
    def __init__(self, message="", _type="info", timeout=1000):
        super().__init__()
        self.type = _type
        self.message = message
        self.timeout = timeout

    def run(self):
        try:
            root = Tk()
            root.withdraw()
            root.after(self.timeout, root.destroy)
            if type == 'info':
                messagebox.showinfo('Info', self.message, master=root)
            elif type == 'warning':
                messagebox.showwarning('Warning', self.message, master=root)
            elif type == 'error':
                messagebox.showerror('Error', self.message, master=root)
        except ValueError as e:
            print(e)
            pass


class PlayBeep(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        playsound("beep.wav", block=False)


class VideoGet:
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


class VideoShow:
    def __init__(self, frame=None):
        super().__init__()
        self.frame = frame
        self.stopped = False
        self.detected = []
        self.cleanFlag = False
        self.startTime = 0

    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def setCleanSchedule(self):
        if not self.cleanFlag:
            self.startTime = time.time() + CLEAN_UP_DELAY
            self.cleanFlag = True

    def show(self):
        global videoLabelImage
        while not self.stopped:
            if self.cleanFlag:
                if time.time() > self.startTime:
                    self.cleanFlag = False
                    self.detected = []

            img = self.frame
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

                    if studentId not in self.detected:
                        self.detected.append(studentId)
                        self.setCleanSchedule()
                        thread = PlayBeep()
                        thread.start()

            cv2.imshow("Video", img)
            if cv2.waitKey(1) == ord("q"):
                self.stopped = True

    def stop(self):
        self.stopped = True


class Detector(Thread):
    def __init__(self):
        super().__init__()
        self.videoGetter = VideoGet(SOURCE).start()
        self.videoShower = VideoShow(self.videoGetter.frame).start()

    def run(self):
        while True:
            if self.videoGetter.stopped or self.videoShower.stopped:
                self.videoShower.stop()
                self.videoGetter.stop()
                break

            frame = self.videoGetter.frame
            self.videoShower.frame = frame


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("SkoolTech Pro")
        self.geometry("1360x720")
        self.configure(bg="white")
        self.resizable(False, False)
        self.update()
        self.attributes("-fullscreen", True)

        self.windowWidth = self.winfo_width()
        self.windowHeight = self.winfo_height()
        self.frameWidth = (self.windowWidth / 6) - 10
        self.frameHeight = (self.windowHeight / 2) - 65
        self.framePadY = 5
        self.framePadX = 5
        self.color = "#000080"

        self.headerFrame = tk.Frame(self)
        self.timeLabel = Label(self.headerFrame)
        self.dateLabel = Label(self.headerFrame)
        self.schoolNameLabel = Label(self.headerFrame)
        self.schoolAddressLabel = Label(self.headerFrame)

        self.frame1 = tk.Frame(self)
        self.frame11 = tk.Frame(self)
        self.videoLabel = Label(self.frame11)

        self.footerFrame = tk.Frame(self)
        self.footerLabel = Label(self.footerFrame)

        self.CreateHeader()
        self.CreateBody()
        self.CreateFooter()

        self.Initialize()
        self.GetSchoolDetail()
        self.UpdateDate()
        self.UpdateTime()

    def CreateHeader(self):
        self.headerFrame.configure(width=self.windowWidth, height=80, bg="#000080")
        self.headerFrame.grid(row=0, column=0, columnspan=6)
        self.timeLabel.configure(font=("calibre light", 35), fg="white", text="88:88 AM")
        self.timeLabel.place(x=self.windowWidth - 230, y=25)
        self.dateLabel.configure(font=("calibre light", 18), fg="white", text="FEB 9, 1986")
        self.dateLabel.place(x=self.windowWidth - 190, y=0)
        self.schoolNameLabel.configure(font=("calibri light", 25), fg="white", text="SkoolTech Solution Academy")
        self.schoolNameLabel.place(x=85, y=10)
        self.schoolAddressLabel.configure(font=("calibri light", 12), fg="white",
                                          text="Block 16 lot 18-19 Belair Subdivision Buru-un Iligan City")
        self.schoolAddressLabel.place(x=85, y=45)

    def CreateBody(self):
        self.frame1.configure(width=self.frameWidth, height=self.frameHeight, bg="#FFFFFF")
        self.frame1.grid(row=1, column=0, pady=self.framePadY, padx=self.framePadX)

        self.frame11.configure(width=(self.frameWidth * 2) + 10, height=self.frameHeight, bg="#FFFFFF")
        self.frame11.grid(row=2, column=4, pady=self.framePadY, padx=self.framePadX, columnspan=2)
        self.frame11.pack_propagate(False)

        self.videoLabel.configure(width=int(self.frameWidth * 2), height=int(self.frameHeight) - 10, bg="#000080")
        self.videoLabel.pack(pady=5)

    def CreateFooter(self):
        self.footerFrame.configure(width=self.windowWidth, height=30, bg="#000080")
        self.footerFrame.grid(row=3, column=0, columnspan=6)
        self.footerFrame.pack_propagate(False)
        self.footerLabel.configure(text="POWERED BY SKOOLTECH SOLUTIONS", fg="white")
        self.footerLabel.pack(pady=5)

    def Initialize(self):
        thread = InitFaceRecognition()
        thread.start()
        self.InitFaceRecognitionMonitor(thread)

    def GetSchoolDetail(self):
        url = API_LINK + "/school.php"
        data = {'id': SCHOOL_ID}
        thread = ApiCall(url=url, data=data)
        thread.start()
        self.GetSchoolDetailMonitor(thread)

    def UpdateDate(self):
        global updateDateFlag
        updateDateFlag = True
        today = date.today()
        year = today.year
        month = months[today.month]
        day = today.day
        dateString = month + " " + str(day) + ", " + str(year)
        self.dateLabel.configure(text=dateString)

    def UpdateTime(self):
        global updateDateFlag
        string = strftime("%H:%M:%S")
        self.timeLabel.config(text=string)
        self.timeLabel.after(1000, self.UpdateTime)
        if string == "00:00:01" and not updateDateFlag:
            self.updateDate()
        if string == "01:00:00" and updateDateFlag:
            updateDateFlag = False

    """def UpdateVideo(self):
        global videoLabelImage
        img = videoLabelImage
        if img is not None:
            self.videoLabel.configure(image=img)
            self.videoLabel.image = img
        self.after(70, lambda: self.UpdateVideo())"""

    def MarkAttendance(self, _id):
        url = API_LINK + "/attendance.php"
        data = {'schoolid': SCHOOL_ID, 'studentid': _id}
        thread = ApiCall(url=url, data=data)
        thread.start()
        self.MarkAttendanceMonitor(thread)

    # *********** Monitors ************
    def InitFaceRecognitionMonitor(self, thread):
        global encodeListKnown
        if thread.is_alive():
            self.after(100, lambda: self.InitFaceRecognitionMonitor(thread))
        else:
            encodeListKnown = thread.knownList
            thread = Detector()
            thread.start()
            #self.UpdateVideo()

    def GetSchoolDetailMonitor(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.GetSchoolDetailMonitor(thread))
        else:
            response = thread.response
            resp = response.split("*_*")
            if len(resp) > 0:
                if resp[0] == "true":
                    self.RenderSchoolDetail(resp[1])
                elif resp[0] == "false":
                    thread = ShowMessage(resp[1], "warning", 1000)
                    thread.start()
                else:
                    thread = ShowMessage(response, "error", 1000)
                    thread.start()

    def MarkAttendanceMonitor(self, thread):
        if thread.is_alive():
            self.after(100, lambda: self.MarkAttendanceMonitor(thread))
        else:
            response = thread.response
            resp = response.split("*_*")
            if len(resp) > 0:
                if resp[0] == "true":
                    self.RenderStudentDetail(resp[1])
                elif resp[0] == "false":
                    thread = ShowMessage(message=resp[1], _type="warning", timeout=1000)
                    thread.start()
                else:
                    thread = ShowMessage(message=response, _type="error", timeout=1000)
                    thread.start()

    # *********** Renderer ************
    def RenderSchoolDetail(self, data):
        details = json.loads(data)
        base64Image = details[0]["image"].split(",")
        image = base64Image[1]
        name = details[0]["name"]
        address = details[0]["address"]
        self.color = details[0]["color"]

        self.headerFrame.configure(bg=self.color)
        self.timeLabel.configure(bg=self.color)
        self.dateLabel.configure(bg=self.color)
        self.schoolNameLabel.configure(bg=self.color)
        self.schoolAddressLabel.configure(bg=self.color)
        self.footerLabel.configure(bg=self.color)
        self.footerFrame.configure(bg=self.color)
        self.frame11.configure(bg=self.color)

        self.schoolNameLabel.configure(text=name)
        self.schoolAddressLabel.configure(text=address)

        # Create logo label container
        img = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))
        resized_image = img.resize((70, 70))

        logo = ImageTk.PhotoImage(resized_image)
        label = Label(self.headerFrame, image=logo)
        label.place(x=5, y=5)
        label.image = logo

    def RenderStudentDetail(self, data):
        global detectedList
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
        self.RenderDetected(detectedList)

    def RenderDetected(self, data):
        i = 0
        for _list in reversed(data):
            _image = _list[0]
            name = _list[1]
            _type = _list[2]
            activity = _list[5]

            if i > 5:
                studentFrame = tk.Frame(self, width=self.frameWidth, height=self.frameHeight, bg=self.color)
                studentFrame.grid(row=2, column=i - 6, pady=self.framePadY, padx=self.framePadX)
            else:
                studentFrame = tk.Frame(self, width=self.frameWidth, height=self.frameHeight, bg=self.color)
                studentFrame.grid(row=1, column=i, pady=self.framePadY, padx=self.framePadX)

            i += 1

            _img = Image.open(io.BytesIO(base64.decodebytes(bytes(_image, "utf-8"))))
            imageWidth = int(self.frameWidth - 12)
            resized_image = _img.resize((imageWidth, imageWidth))
            studentImage = ImageTk.PhotoImage(resized_image)
            studentImageLabel = tk.Label(studentFrame, image=studentImage)
            studentImageLabel.place(x=5, y=5)
            studentImageLabel.image = studentImage
            studentName = tk.Label(studentFrame, anchor="center", text=name, width=25)
            studentName.place(x=5, y=imageWidth + 10)
            studentDetails = tk.Label(studentFrame, anchor="center", text=_type + " - " + activity, width=25,
                                      fg="white",
                                      bg=color)
            studentDetails.place(x=5, y=imageWidth + 32)


if __name__ == "__main__":
    app = App()
    app.mainloop()

