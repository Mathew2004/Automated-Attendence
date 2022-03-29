import cv2
import numpy as np
import face_recognition
import os
import datetime
import gspread
import datetime
import requests
import pandas as pd
import json
import pyttsx3

def talk(speak):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')  # getting details of current voice
    engine.setProperty('voice', voices[1].id)
    engine.say(speak)
    engine.runAndWait()

def send_msg(text):
    token = '5278107863:AAHQfWg2Bhyw1rgnRlJ9qqUQPTOpjjunlrw'
    chat_id = '1144510960'

    url_req = "https://api.telegram.org/bot"+token+"/sendMessage"+"?chat_id="+chat_id+"&text="+text
    results = requests.get(url_req)
    #print(results.json())





#Google Sheets
gc = gspread.service_account(filename='credential.json')
sh = gc.open_by_key('1zRiqIuYzLhhZfH77NonoQTWlDbQZXQdcn3vU4UcDgZg')
worksheet = sh.sheet1



path = 'ImageAttendence'
images = []
classNames = []
mylist = os.listdir(path)
print(mylist)
for cl in mylist:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findencodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
'''
def markAttendence(name):
    with open('attendencelist.csv', 'r+') as f:
        myDataList = f.readline()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.datetime.now()
            dString = now.strftime('%x')
            tString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dString},{tString}')

'''
encodelistKnown = findencodings(images)
print("Encoding Complete")


cap = cv2.VideoCapture(1)
i = 0
while True:
    success,img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
    now = datetime.datetime.now()
    date = now.strftime('%D')
    time = now.strftime("%I:%M:%S %p")

    for encodeFace,faceLoc in zip(encodeCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodelistKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodelistKnown,encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)


        if matches[matchIndex]:
            print(matches[matchIndex])
            #SheetList = []
            name = classNames[matchIndex].upper()
            #SheetList.append(name)
            #print(SheetList)

            y1,x2,y2,x1 = faceLoc
            #y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,(y2-35)),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_DUPLEX, 1.0,(255,255,255),2)
            user = [name, date, time]
            worksheet.append_row(user)




            #worksheet.drop_duplicates()
            #markAttendence(name)
        else:
            y1, x2, y2, x1 = faceLoc
            # y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.rectangle(img, (x1, (y2 - 35)), (x2, y2), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, "Unknown", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)
            user = ["Unknown", date, time]
            worksheet.append_row(user)
            cv2.imwrite('Unknown/Unkown' + str(i) + '.jpg', img)
            talk("An Unkown Person Found!")
            #Uploading Photos on Gdrive
            headers = {
                "Authorization": "Bearer ya29.A0ARrdaM_mMXkPWAlK6aVlI1ZeWCLgErIN0cBqyCRCcNh0mXLcyvptayJJRJYy5luuVHLrBu-ZpeJvM2RBPY6GW5U5yVM4gl1DDTUEw96NRnuctrih7VCrndIkmOEYkA4JpZc8P0dku2WIbpfiu8Y6NysUu6de"}

            para = {
                "name": "Unkown" + str(i) + ".jpg",
                "parents": ["1adFWxxKK3uBDFk-uOOPxfJtIV2upqgt2"],
            }
            files = {
                'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
                'file': open("Unknown/Unkown" + str(i) + ".jpg", "rb")
            }


            r = requests.post(
                "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
                headers=headers,
                files=files
            )
            print(r.text)

            i += 1
            send_msg("🛑🛑 Alert 🛑🛑 \n\nAn Unknown Person Entires Your Room \n\n "+
                     "View Unknown Faces: https://drive.google.com/drive/folders/1adFWxxKK3uBDFk-uOOPxfJtIV2upqgt2 \n\nn"+"Current Time: "+time )


    cv2.imshow('Webcam',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
cap.release()
# Destroy all the windows
cv2.destroyAllWindows()

#Send Results In Telegram
dataframe = pd.DataFrame(worksheet.get_all_records())
df = dataframe.drop_duplicates(subset=['Name', 'Date'], keep='last')
#index = df.index
#count_row = len(index)
rd = str(df)

send_msg("These are Unique Result \n\n"+rd + "\n\n"+
         " To view Full Sheets: rebrand.ly/e4k7aoi \n\n"+
         "View Unknown Faces: https://drive.google.com/drive/folders/1adFWxxKK3uBDFk-uOOPxfJtIV2upqgt2" )
