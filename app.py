from flask import Flask,render_template,request,Response,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
import cv2
from datetime import datetime
import time
import io
from PIL import Image
import base64
import snap7
import snap7.util as su
#initialization:
counter_state = 0
#192.168.0.241
encoded_img_data= base64.b64encode(b'abc')
global frame, success
cap = cv2.VideoCapture(0)
cv2.useOptimized()
#implement image processing here:
def image_processing(img):
    detected_cap = False
    detected_label = False
    cap_y = 180
    cap_x = 250
    cap_h = 80
    cap_w = 120
    label_x = 265
    label_y = 330
    label_w = 120
    label_h = 120
    # TODO: CAP IMAGE PROCESSING
    roi_label = img[label_y:(label_y + label_h), label_x:(label_x + label_w)]
    roi_cap = img[cap_y:(cap_y + cap_h), cap_x:(cap_x + cap_w)]
    # cap image processing:
    hsv_cap = cv2.cvtColor(roi_cap, cv2.COLOR_BGR2HSV)
    hsv_blurred_cap = cv2.GaussianBlur(hsv_cap, (5, 5), 3)
    color_mask_cap = cv2.inRange(hsv_blurred_cap, (40, 35, 0), (179, 255, 250))
    eroded_cap = cv2.erode(color_mask_cap, (3, 3), iterations=1)
    dialated_cap = cv2.dilate(eroded_cap, (3, 3), iterations=1)
    # edge detection:
    edges_cap = cv2.Canny(dialated_cap, 200, 230)
    dil_edges_cap = cv2.dilate(edges_cap, (3, 3))
    contours_cap, hirearchy_cap = cv2.findContours(dil_edges_cap, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # drawing on original frame cap:
    for i in range(len(contours_cap)):
        if 850 < cv2.contourArea(contours_cap[i]) < 1200:
            cv2.drawContours(img, contours_cap, i, (0, 255, 0), 1, offset=(250, 180))
            cv2.putText(img, "Cap detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
            detected_cap = True
            break
        elif 0 <= cv2.contourArea(contours_cap[i]) < 250:
            pass
        else:
            detected_cap = False
            cv2.putText(img, "Cap not detected", (400, 400), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
    # TODO:label image processing:
    blurr_roi_label = cv2.GaussianBlur(roi_label, (5, 5), 3)
    hsv_label = cv2.cvtColor(blurr_roi_label, cv2.COLOR_BGR2HSV)
    label_mask = cv2.inRange(hsv_label, (50, 0, 0), (179, 255, 180))
    eroded_label_mask = cv2.erode(label_mask, (3, 3), iterations=1)
    dil_label_mask = cv2.dilate(eroded_label_mask, (3, 3), iterations=3)
    # edge detection:
    edges_label = cv2.Canny(dil_label_mask, 200, 230)
    dil_edges_label = cv2.dilate(edges_label, (3, 3))
    contours_label, hirearchy_label = cv2.findContours(dil_edges_label, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # drawing on original frame label:
    for i in range(len(contours_label)):
        if 4000 <= cv2.contourArea(contours_label[i]) < 4500:
            cv2.drawContours(img, contours_label, i, (0, 255, 0), 1, offset=(265, 327))
            cv2.putText(img, "label detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 2)
            detected_label = True
            break
        elif 0 <= cv2.contourArea(contours_cap[i]) < 500:
            pass
        else:
            cv2.drawContours(img, contours_label, i, (0, 0, 255), 1, offset=(265, 327))
            cv2.putText(img, "label not detected", (150, 400), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2)
            detected_label = False
    return img, detected_cap, detected_label

#checking memory bit:
def check_plc_mem_bit(CLIENT, BYTE, BIT):
    bit_offset = 7
    state = CLIENT.mb_read(BYTE, 1)  # Read starting from byte-1 , a byte
    bits = bin(state[0]).split("b")[1]
    while len(bits) <= 7:
        bits = "0" + bits
    if bits[bit_offset - BIT] == "1":  # if M1.0 is set do something:
        return True
    elif bits[bit_offset - BIT] == "0":
        return False

def get_plc_memory_word(CLIENT,START_BYTE):
    byte = CLIENT.mb_read(START_BYTE, 2)
    int_ret = su.get_int(byte, 0)
    return int_ret
def video_stream():
    global encoded_img_data, counter_state
    while True:
        try:
            state_M_1_0 = check_plc_mem_bit(client, 1, 0)
            counter_state = get_plc_memory_word(client,2)
            if state_M_1_0 :
                success, frame = cap.read()
                if success:
                    processed, detected_cap, detected_label = image_processing(frame)
                    img = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                    im = Image.fromarray(img)
                    data = io.BytesIO()
                    im.save(data, "JPEG")
                    encoded_img_data = base64.b64encode(data.getvalue())
        except Exception:
            pass
        time.sleep(0.1)
        #NOTE: sleep  set to 0.01 because of plc program timer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///statistics.db'
#initialize database
db = SQLAlchemy(app)
class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True) #Primary key= True ---> all keys unique
@app.route("/",methods =['POST' , 'GET'])
def index():
    global connected_before, client, cpu
    if request.method == 'POST':
        RACK = request.form['rack_selector']
        IP = request.form['ip_adress']
        N = request.form['cpu_slot_selector']
        client = snap7.client.Client()
        client.connect(IP, int(RACK), int(N))
        is_connected = client.get_connected()
        if is_connected:
            return redirect(url_for('connected_to_plc'))
        else:
            #return redirect(url_for('connected_to_plc'))  #for testing without connecting to plc
            return render_template("index.html")

    else:
        return render_template("index.html")

@app.route("/connected",methods =["GET"])
def connected_to_plc():
    global encoded_img_data, bottle_count
    return render_template("connected.html",img_data1 = encoded_img_data.decode('utf-8') ,count =counter_state )

#processed image feed
@app.route("/image")
def image_feed():
    return Response(video_stream(),mimetype='multipart/x-mixed-replace;boundary=frame')

if __name__ == "__main__" :
    app.run(host="132.186.155.82", port= "9999",debug=True)
