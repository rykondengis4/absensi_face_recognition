import cv2
import numpy as np
import face_recognition

imgTony = face_recognition.load_image_file("img/iki dalanggo.jpeg")
imgTony = cv2.cvtColor(imgTony, cv2.COLOR_BGR2RGB)
imgTest = face_recognition.load_image_file("img/ferdiyanto wartabone.jpeg")
imgTest = cv2.cvtColor(imgTest, cv2.COLOR_BGR2RGB)

faceLoc = face_recognition.face_locations(imgTony)[0]
encodeTony = face_recognition.face_encodings(imgTony)[0]
cv2.rectangle(imgTony, (faceLoc[3], faceLoc[0]),(faceLoc[1], faceLoc[2]), (255,0,255), 2)

faceLocTest = face_recognition.face_locations(imgTest)[0]
encodeTest = face_recognition.face_encodings(imgTest)[0]
cv2.rectangle(imgTest, (faceLocTest[3], faceLocTest[0]),(faceLocTest[1], faceLocTest[2]), (255,0,255), 2)

result = face_recognition.compare_faces([encodeTony], encodeTest)
faceDis = face_recognition.face_distance([encodeTony], encodeTest)

if result[0]:
    color = (0, 255, 0)  # Hijau jika cocok
else:
    color = (0, 0, 255)  # Merah jika tidak cocok

cv2.putText(imgTest, f'{result} {round(faceDis[0], 2)} ', (50, 50), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, color, 2)


# cv2.putText(imgTest, f'{result} {round(faceDis[0], 2)} ', (50,50), cv2.FONT_HERSHEY_COMPLEX_SMALL,1,(0,0,255),2)
print(result, faceDis)

cv2.imshow("tony stark", imgTony)
cv2.imshow("tony stark test", imgTest)

cv2.waitKey(0)