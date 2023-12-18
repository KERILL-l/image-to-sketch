from io import BytesIO
from flask import Flask, render_template, send_file, request,  url_for, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/home/kirill/new_img_to_scetch/static/upload'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
db = SQLAlchemy(app)


def alg(filename: str):
    img = cv2.imread(filename)
    gr_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    (h, w) = img.shape[:2]

    # display image properties
    print("width: " + str(w))
    print("height: " + str(h))

    edge_img = cv2.Canny(img,175,50)
    edge_img2 = cv2.Canny(gr_img, 175, 50)

    inv_img = cv2.bitwise_not(gr_img)

    blur_img1 = cv2.GaussianBlur(inv_img, (13,13), 0)
    blur_img2 = cv2.GaussianBlur(inv_img, (21,21), 0)

    invert_blur1 = cv2.bitwise_not(blur_img1)
    invert_blur2 = cv2.bitwise_not(blur_img2)


    blur_img = cv2.add(blur_img1, blur_img2)

    invert_blur = cv2.bitwise_not(blur_img)

    # Convert Image Into sketch
    sketch1 = cv2.divide(gr_img, invert_blur1, scale=256.0)
    sketch2 = cv2.divide(gr_img, invert_blur2, scale=256.0)

    sketch = sketch1 + sketch2
    im = Image.fromarray(sketch)
    im.save(filename)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/about')
def howto():
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'static/uploads/')
        print(target)
        if not os.path.isdir(target):
            os.mkdir(target)

        print(request.files.getlist("file"))
        for upload in request.files.getlist("file"):
            print(upload)
            print("{} is the file name".format(upload.filename))
            filename = upload.filename
            destination = "".join([target, filename])
            print ("Accept incoming file:", filename)
            print ("Save it to:", destination)
            upload.save(destination)

            
        return render_template('converter.html', image = filename)
    return render_template('converter.html', image = '2.jpg')

@app.route('/get_image/<image_name>')
def get_image(image_name):
    return send_file('/home/kirill/new_img_to_scetch/static/uploads/{image_name}', mimetype='image')

@app.route('/download/<upload_file>')
def download(upload_file):
    alg(f'/home/kirill/new_img_to_scetch/static/uploads/{upload_file}')
    return send_file(f'/home/kirill/new_img_to_scetch/static/uploads/{upload_file}', download_name= upload_file, as_attachment=True)
    

if __name__ == '__main__':
    app.run()