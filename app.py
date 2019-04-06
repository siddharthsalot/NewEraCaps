from flask import Flask, flash, current_app, request
from flask import render_template, url_for
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from flask_wtf import FlaskForm
import os
import secrets
from PIL import Image
from sys import stderr
#!"C:\anaconda\Anconda\python.exe"
#import cgi
#import cgitb
from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np
import imutils
import cv2
from keras import backend as K

app = Flask(__name__)

app.config['SECRET_KEY'] = '1d7ce38b6bfe845340bbd1ac902cbe4f'

class TestImgForm(FlaskForm):
    picture = FileField("Update Logo", validators=[FileAllowed(['jpg','jpeg', 'png'])])
    submit = SubmitField("Run")

def validate_image(image):
    image = cv2.imread(image)
    #image=cv2.imread(fileitem)
    width,height=image.shape[:2]
    orig = image.copy()

    image = cv2.resize(image, (96, 96))

    image = image.astype("float") / 255.0
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    model = load_model("newera.model")
    (notbrand, brand) = model.predict(image)[0]
    K.clear_session()
    proba = brand if brand > notbrand else notbrand
    label = "Brand" if brand > notbrand else "Not Brand"
    return round(proba*100,2),label


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, 'static\images', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)
    likelihood_score,label = validate_image(picture_path)
    return likelihood_score,label,picture_fn


@app.route("/",methods=['GET', 'POST'])
@app.route("/home",methods=['GET', 'POST'])
def test_img():
    form = TestImgForm()
    likelihood_score = 0
    label='Brand/Not Brand'
    if request.method == "POST":
        likelihood_score,label,picture_fn = save_picture(form.picture.data)
        return render_template("home.html", form=form, score=likelihood_score,bd=label,picture = picture_fn)
    else:
        return render_template("home.html", form=form)
 
if __name__ == "__main__":
    app.run(debug=True)
