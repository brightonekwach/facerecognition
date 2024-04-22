# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import db
#
# cred = credentials.Certificate("serviceAccountKey.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': "https://faceattendancerealtime-6243b-default-rtdb.firebaseio.com/"
# })
#
# ref = db.reference('Students')
#
# data = {
#     "IN130006620":
#         {
#             "name": "Japheth Onyango",
#             "course": "Computer Science",
#             "starting_year": 2020,
#             "total_attendance": 6,
#             "year": 4,
#             "last_attendance_time": "2024-2-24 00:54:34"
#         },
#     "963852":
#         {
#             "name": "Elon Musk",
#             "course": "Physics",
#             "starting_year": 2018,
#             "total_attendance": 10,
#             "year": 4,
#             "last_attendance_time": "2024-2-24 00:54:34"
#         },
#     "IN130007620":
#         {
#             "name": "Brighton Kwach",
#             "course": "Computer Science",
#             "starting_year": 2020,
#             "total_attendance": 6,
#             "year": 4,
#             "last_attendance_time": "2024-2-24 00:54:34"
#         },
#
#
#
#
# }
#
# for key, value in data.items():
#     ref.child(key).set(value)
import tkinter as tk
from tkinter import filedialog
from firebase_admin import storage
from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
import os

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancerealtime-6243b-default-rtdb.firebaseio.com/",
    'storageBucket': "faceattendancerealtime-6243b.appspot.com"
})

# Reference to Firebase Database
ref = db.reference('Students')

# Function to handle uploading data and images
def upload_data():
    # Get data from entries
    student_id = student_id_entry.get()
    name = name_entry.get()
    course = course_entry.get()
    starting_year = int(starting_year_entry.get())
    total_attendance = int(total_attendance_entry.get())
    year = int(year_entry.get())


    # Prepare data dictionary
    data = {
        "name": name,
        "course": course,
        "starting_year": starting_year,
        "total_attendance": total_attendance,
        "year": year,
    }

    # Upload data to Firebase Database
    ref.child(student_id).set(data)

    # Upload image to Firebase Storage if selected
    if image_path:
        bucket = storage.bucket()
        blob = bucket.blob("images/" + os.path.basename(image_path))
        blob.upload_from_filename(image_path)

# Function to handle image selection
def select_image():
    global image_path
    image_path = filedialog.askopenfilename()
    image_label.config(text=image_path)

# Create Tkinter window
root = tk.Tk()
root.title("Upload Data to Firebase")

# Create labels and entries for data
tk.Label(root, text="Student ID:").grid(row=0, column=0)
student_id_entry = tk.Entry(root)
student_id_entry.grid(row=0, column=1)

tk.Label(root, text="Name:").grid(row=1, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=1, column=1)

tk.Label(root, text="Course:").grid(row=2, column=0)
course_entry = tk.Entry(root)
course_entry.grid(row=2, column=1)

tk.Label(root, text="Starting Year:").grid(row=3, column=0)
starting_year_entry = tk.Entry(root)
starting_year_entry.grid(row=3, column=1)

tk.Label(root, text="Total Attendance:").grid(row=4, column=0)
total_attendance_entry = tk.Entry(root)
total_attendance_entry.grid(row=4, column=1)

tk.Label(root, text="Year:").grid(row=5, column=0)
year_entry = tk.Entry(root)
year_entry.grid(row=5, column=1)


# Image selection button and label
tk.Button(root, text="Select Image", command=select_image).grid(row=7, column=0)
image_label = tk.Label(root, text="")
image_label.grid(row=7, column=1)

# Upload button
upload_button = tk.Button(root, text="Upload Data", command=upload_data)
upload_button.grid(row=8, columnspan=2)

root.mainloop()

