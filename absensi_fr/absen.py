import cv2
import face_recognition
import os
import numpy as np
import mysql.connector
from datetime import datetime
import signal
import requests
import time
import threading

# database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    database="absensi_wajah"
)

mycursor = db_connection.cursor()

# path = "img data"
path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img data'))
images = []
studentName = []
myList = os.listdir(path)
print(myList)

firstAbsenceTimes = {}

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    studentName.append(os.path.splitext(cl)[0])
    firstAbsenceTimes[os.path.splitext(cl)[0]] = None

print(studentName)

def findEncodings(images):
    encodingList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodingList.append(encode)
    return encodingList

encodeListKnown = findEncodings(images)
print("encoding complete")

current_date = datetime.now().strftime('%Y-%m-%d')
absenceTime = datetime.now().strftime('%H:%M:%S')

cam = cv2.VideoCapture(0)

print(current_date)

app_running = True

def start_camera():
    url = "http://127.0.0.1:8000/start"
    response = requests.post(url)
    print(response.json())

def stop_camera():
    url = "http://127.0.0.1:8000/stop"
    response = requests.post(url)
    print(response.json())

def stop_application():
    global app_running
    cam.release()
    cv2.destroyAllWindows()
    app_running = False


def handle_exit(signal, frame):
    print("Exiting...")
    stop_application()
    exit(0)

def get_nim_by_id(id_mahasiswa):
    response = requests.get("http://127.0.0.1:8000/nim", params={"id": id_mahasiswa})
    nim_result = response.json()
    return nim_result

def check_absensi(id_mahasiswa, tanggal_absensi):
    response = requests.get("http://127.0.0.1:8000/check_absensi", params={"id_mahasiswa": id_mahasiswa, "tanggal_absensi": tanggal_absensi})
    result = response.json()
    return result.get("count", 0)

def insert_absensi(tanggal_absensi, id_mahasiswa, waktu_masuk):
    url = "http://127.0.0.1:8000/insert_absensi"
    data = {
        "tanggal_absensi": tanggal_absensi,
        "id_mahasiswa": id_mahasiswa,
        "waktu_masuk": waktu_masuk
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        print(result["message"])
    except requests.RequestException as e:
        print(f"Error inserting absensi: {e}")


def process_frame():
    global app_running
    start_time = time.time()

    while app_running:

        if time.time() - start_time > 20:
            stop_camera()
            stop_application()
            break

        success, img = cam.read()
        imgS = cv2.resize(img,(0,0), None,0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurlFrame = face_recognition.face_locations(imgS)
        encodeCurlFrame = face_recognition.face_encodings(imgS, faceCurlFrame)

        dates_printed = set()


        if not faceCurlFrame:
            stop_camera()
            stop_application()
            break

        else:
            for encodeFace, faceLoc in zip(encodeCurlFrame, faceCurlFrame):
                compere = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if compere[matchIndex]:
                    name = studentName[matchIndex].upper()

                    if current_date not in dates_printed:
                        response = requests.get("http://127.0.0.1:8000/mahasiswa", params={"name": name})
                        result = response.json()


                        if result:
                            id_mahasiswa = result[0]

                            nim_result = get_nim_by_id(id_mahasiswa)

                            if nim_result:
                                nim = nim_result[0]

                                y1, x2, y2, x1 = faceLoc
                                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.rectangle(img, (x1, y2 + 60), (x2, y2 - 3), (0, 255, 0), cv2.FILLED)
                                cv2.putText(img, f"{name}", (x1 + 6, y2 + 15), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                            (255, 255, 255), 2)
                                cv2.putText(img, f"{nim}", (x1 + 6, y2 + 40), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                            (255, 255, 255), 2)
                                cv2.rectangle(img, (x1, y2 - 5), (x2, y2), (0, 255, 0), 2)

                                count_result = check_absensi(id_mahasiswa, current_date)

                                if count_result == 0:
                                    insert_absensi(current_date, id_mahasiswa, absenceTime)


                cv2.imshow("wajah", img)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or cv2.getWindowProperty("wajah", cv2.WND_PROP_VISIBLE) < 1:
                    stop_camera()
                    stop_application()
                    break

        del img, imgS

signal.signal(signal.SIGINT, handle_exit)
frame_thread = threading.Thread(target=process_frame)
frame_thread.start()
frame_thread.join()