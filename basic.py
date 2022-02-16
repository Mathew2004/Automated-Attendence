import cv2
import numpy as np
import face_recognition

imgElon = face_recognition.load_image_file('image-basic/Elon Mask.jpeg')
imgElon = cv2.cvtColor(imgElon,cv2.COLOR_BGR2RGB)
imgTest = face_recognition.load_image_file('image-basic/Elon test.jpg')
imgTest = cv2.cvtColor(imgTest,cv2.COLOR_BGR2RGB)

faceLoc = face_recognition.face_locations(imgElon)[0]
encodeElon = face_recognition.face_encodings(imgElon)[0]
cv2.rectangle(imgElon,(faceLoc[3],faceLoc[0]),(faceLoc[1],faceLoc[2]),(255,0,0),2)

faceLocTest = face_recognition.face_locations(imgTest)[0]
encodeTest = face_recognition.face_encodings(imgTest)[0]
cv2.rectangle(imgTest,(faceLocTest[3],faceLocTest[0]),(faceLocTest[1],faceLocTest[2]),(255,0,0),2)

results = face_recognition.compare_faces([encodeElon],encodeTest)
facedistance = face_recognition.face_distance([encodeElon],encodeTest)
print(results,facedistance)

cv2.imshow("ImgElon",imgElon)
cv2.imshow("imgTest",imgTest)
cv2.waitKey(0)