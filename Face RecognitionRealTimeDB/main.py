import os
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import csv
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-6243b-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-6243b.appspot.com"
})

bucket = storage.bucket()

# Function to log login time
def log_login_time(user_id):
    with open('login.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, datetime.now()])

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackrground = cv2.imread('Resources/background.png')

# importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

#  Load the encoding file
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
# print(studentIds)

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackrground[162:162+480,55:55+640] = img
    imgBackrground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("faceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("matchIndex", matchIndex)

        if matches[matchIndex]:
            # print("Known face detected")
            # print(studentIds[matchIndex])
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4,y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackrground = cvzone.cornerRect(imgBackrground, bbox, rt=0)
            id = studentIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1

        if counter!= 0:


            if counter == 1:
                # get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #  get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                imgStudent_resized = cv2.resize(imgStudent, (216, 216))
                #update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  '%Y-%m-%d %H:%M:%S')
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                ref = db.reference(f'Students/{id}')
                studentInfo['total_attendance'] += 1
                ref.child('total_attendance').set(studentInfo['total_attendance'])
                ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if 5<counter<10:
                modeType = 2

            imgBackrground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if counter<=5:
                cv2.putText(imgBackrground, str(studentInfo['total_attendance']), (861, 125),
                            cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                cv2.putText(imgBackrground, str(studentInfo['course']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(imgBackrground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.4, (255, 255, 255), 1)
                cv2.putText(imgBackrground, str(studentInfo['year']), (1025, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackrground, str(studentInfo['starting_year']), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                offset = (414-w)//2
                cv2.putText(imgBackrground, str(studentInfo['name']), (808 + offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                imgBackrground[175:175+216, 909:909+216] = imgStudent_resized

            counter += 1

            if counter>=10:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackrground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackrground)
    cv2.waitKey(1)