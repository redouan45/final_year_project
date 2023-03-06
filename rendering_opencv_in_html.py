from flask import Flask, render_template
from PIL import Image
import base64
import cv2
import io
import time
from threading import *


app = Flask(__name__)
cap = cv2.VideoCapture(0)
cv2.useOptimized()
def image_thread():
    while True:
        img = cap.read()[1]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img)
        print(im)
        data = io.BytesIO()
        im.save(data, "JPEG")
        encoded_img_data = base64.b64encode(data.getvalue())
        time.sleep(0.02)
        return encoded_img_data

@app.route('/')
def hello_world():

    t1 = Thread(target=image_thread)
    t1.start()
    return render_template("index2.html", img_data=image_thread().decode('utf-8'))


if __name__ == '__main__':
    app.run(host='192.168.1.6',port='9999',debug=True)