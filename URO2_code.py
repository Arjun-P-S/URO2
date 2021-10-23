import cv2 as cv
import numpy as np
import time
import smtplib
import os
from email.mime.text import MIMEText

coords = [[517, 476], [562, 484], [561, 441], [529, 440], [724, 494], [763, 499], [763, 472],
    [730, 466], [921, 508], [966, 510], [967, 483], [928, 472], [1029, 511], [1066, 513],
    [1067, 483], [1028, 479], [1131, 512], [1170, 519], [1165, 481], [1139, 482], [1234, 519],
    [1269, 522], [1270, 495], [1230, 487]]

pH = [[104, 145, 84], [81, 98, 87], [52, 81, 114], [43, 73, 130], [28, 75, 120], [9, 111, 155], [5, 119, 148]] #ph high -> low
sp_gravity = [[14, 134, 110], [23, 123, 96], [25, 118, 116], [30, 101, 100], [40, 61, 86], [69, 79, 80], [108, 61, 58]]#spg high -> low
glucose = [[145, 106, 78], [16, 103, 93], [22, 97, 111], [39, 97, 116], [51, 39, 123], [104, 33, 139]]#High to low
leukocyte = [[146, 105, 85], [144, 76, 106], [159, 21, 138], [165, 15, 144]]#High -> Low
protein =[[116, 28, 79], [102, 40, 106], [57, 9, 123], [31, 55, 124], [30, 87, 134], [26, 93, 143]] #High -> Low
ketone = [[165, 104, 71], [166, 122, 104], [168, 111, 131], [168, 90, 146], [172, 53, 152]]#High -> Low

time.sleep(60)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = 'uromodel2@gmail.com'
GMAIL_PASSWORD = 'uro_unplugged'

def ketone_test(list) :
    H, S, V = list
    if H >= 150 and H < 175 and S < 115 and S >= 95 :
        ketone_result = "Very high (160), consult doctor"
    elif H >= 150 and H < 175 and S < 130 and S >= 115 :
        ketone_result = "High (80), consult doctor"
    elif H > 150 and H <= 180 and S < 120 and S > 105 :
        ketone_result = "Moderate (40)"
    elif H > 150 and H <= 180 and S > 80 and S <= 100 :
        ketone_result = "Small (15)"
    elif H > 150 and H <= 180 and S > 40 and S <= 70 :
        ketone_result = "Traces (5)"
    else :
        ketone_result = "Negative"
    return "Ketone result :" + ketone_result 

def protein_test(list) :
    H, S, V = list
    if H >= 100 and H < 125 :
        protein_result = "Very high (2000), consult doctor"
    elif H >= 90 and H < 110 :
        protein_result = "High (300)"
    elif H >= 40 and H < 70 :
        protein_result = "Moderate (100)"
    elif H >= 20 and H < 40 :
        protein_result = "Low (0-30), traces"
    else :
        protein_result = "Test again"
    return "protein result : " + protein_result

def leukocyte_test(list) :
    H, S, V = list
    if H < 155 and H >= 130 and S > 95 :
        leukocyte_result = "large (500), visit doctor"
    elif H < 155 and S <= 95 and S > 50 :
        leukocyte_result = "moderate (125)"
    elif H < 170 and H >= 140 and S <= 50 and S > 20 :
        leukocyte_result = "small (70)"
    elif H >= 140 and H < 180 and S <= 20 and S > 10 :
        leukocyte_result = "traces (15)"
    else :
        leukocyte_result = "Negative"
    return "leukocyte result :" + leukocyte_result

def glucose_test(list) :
    H, S, V = list
    if H > 130 and S > 65 :
        glucose_result = "very high (2000 mg/dl or more), visit doctor"
    elif H > 90 and S <= 65 :
        glucose_result = "very low"
    elif H >= 5 and H < 18 :
        glucose_result = "high (1000 mg/dl)"
    elif H >= 18 and H < 30 :
        glucose_result = "moderately high (500 mg/dl)"
    elif H >= 30 and H < 45 :
        glucose_result = "moderately low (250 mg/dl) "
    elif H >= 45 and H < 65 :
        glucose_result = "low  (100 mg/dl)"
    else :
        glucose_result = "Negative"
    return "glucose result : " + glucose_result

def sp_gravity_test(list) :
    H, S, V = list
    if H >= 10 and H < 18 :
        sp_gravity_result = "1.030"
    elif H >= 18 and H < 30 :
        sp_gravity_result = "1.025 - 1.020"
    elif H >= 30 and H < 40 :
        sp_gravity_result = "1.015"
    elif H >= 40 and H < 75 :
        sp_gravity_result = "1.010"
    elif H >= 75 and H <= 120 :
        sp_gravity_result = "1.005"
    else :
        sp_gravity_result = "n< = 1.000"
    return "specific gravity result : " + sp_gravity_result

def pH_test(list) :
    H , S, V = list
    if H >= 90 :
        pH_result = "pH is High (8.5), visit the doctor"
    elif H > 60 and H <= 90  :
        pH_result = "pH is moderatly high (8.0), visit the doctor"
    elif H <= 60 and H > 45 :
        pH_result = "pH has a moderatly low value (7.5)"
    elif H <= 45 and H > 35 :
        pH_result = "moderate value (7.0)"
    elif H > 20 and H <= 35 :
        pH_result = "Slighlty acidic (6.5)"
    elif H <= 20 and H > 9 :
        pH_result = "Acidic (6.0)"
    elif H <= 9 :
        pH_result = "Highly acidic (5.0), Visit doctor"
    else:
        pH_result = "Negative"
    return "pH result : " + pH_result

class E_mailer:
    def sendmail(self, recipient, subject, content):
        # Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        # Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        # Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        # Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content.as_string())
                                                                               
        session.quit

#os.system("raspistill -o IMAGE.jpg")
#cv.waitKey(5000)

image = cv.imread("img8.jpg")
image = cv.resize(image, (image.shape[1]//2, image.shape[0]//2))
image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)

i = 0
img = image.copy()
HSV_list = []

while i < len(coords) :
    [x1, y1] = coords[i]
    [x2, y2] = coords[i+1]
    [x3, y3] = coords[i+2]
    [x4, y4] = coords[i+3]
    h_i = np.sqrt((x4-x1)**2 + (y4-y1)**2)
    w_i = np.sqrt((x2-x1)**2 + (y2-y1)**2)
    (Hue, Sat, Val) = cv.split(image_hsv[int(y4): int(y4+h_i) ,int(x4) : int(x4+w_i)])
    Hue_mean = int(np.mean(Hue))
    Sat_mean = int(np.mean(Sat))
    Val_mean = int(np.mean(Val))
    cv.rectangle(img, (x4, y4), (x2, y2), color = (0, 0, 255), thickness=2)
    i = i + 4
    HSV_list.append([Hue_mean, Sat_mean, Val_mean])

ketone_result = ketone_test(HSV_list[0])
protein_result = protein_test(HSV_list[1])
leukocyte_result = leukocyte_test(HSV_list[2])
glucose_result = glucose_test(HSV_list[3])
sp_gravity_result = sp_gravity_test(HSV_list[4])
pH_result = pH_test(HSV_list[5])

Final_Result = [ketone_result, protein_result, leukocyte_result, glucose_result, sp_gravity_result, pH_result]

final_html = """

<p><h1>-------------Thank you for using our services------------</p></h1>
<p>1) %s 
<p>2) %s  
<p>3) %s  
<p>4) %s  
<p>5) %s  
<p>6) %s  """ %(Final_Result[0] , Final_Result[1], Final_Result[2], Final_Result[3], Final_Result[4]
                     , Final_Result[5])
final_send = MIMEText(final_html, "html")
sender = E_mailer()
sendTo = 'urotest0@gmail.com'
emailSubject = "URINALYSIS RESULT"
emailContent = final_send
sender.sendmail(sendTo, emailSubject, emailContent)
