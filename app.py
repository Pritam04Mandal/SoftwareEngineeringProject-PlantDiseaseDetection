from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import tensorflow as tf
import tensorflow as tf

from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession

config = ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.2
config.gpu_options.allow_growth = True
session = InteractiveSession(config=config)
# Keras
# from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask import session
#from gevent.pywsgi import WSGIServer

# Define a flask app
app = Flask(__name__)
app.app_context().push()

# Initialising database Users.db
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///Users.db"
app.config['SECRETKEY']="plantdiseaseproject"
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

# Creating table members
class Members(db.Model):
    email=db.Column(db.String(50), nullable=False, primary_key=True)
    username=db.Column(db.String(50), nullable=False)
    password=db.Column(db.String(50), nullable=False)
    date_registered=db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) ->str:
        return f"{self.email}"

# Model saved with Keras model.save()
MODEL_PATH ='InceptionModel.h5'

# Load your trained model
model = load_model(MODEL_PATH)

def model_predict(img_path, model):
    print(img_path)
    img = image.load_img(img_path, target_size=(224, 224))

    # Preprocessing the image
    x = image.img_to_array(img)
    # x = np.true_divide(x, 255)
    ## Scaling
    x=x/255
    x = np.expand_dims(x, axis=0)
   

    # Be careful how your trained model deals with the input
    # otherwise, it won't make correct prediction!
    # x = preprocess_input(x)
    preds = model.predict(x)
    preds=np.argmax(preds, axis=1)
    if preds==0:
        preds="The Disease is Tomato___Bacterial_spot"
    elif preds==1:
        preds="The Disease is Tomato___Early_blight"
    elif preds==2:
        preds="The Disease is Tomato___Late_blight"
    elif preds==3:
        preds="Te Disease is Tomato___Leaf_Mold"
    elif preds==4:
        preds="The Disease is Tomato___Septoria_leaf_spot"
    elif preds==5:
        preds="The Disease is Tomato___Spider_mites Two-spotted_spider_mite"
    elif preds==6:
        preds="The Disease is Tomato___Target_Spot"
    elif preds==7:
        preds="The Disease is Tomato___Tomato_Yellow_Leaf_Curl_Virus"
    elif preds==8:
        preds="The Disease is Tomato___Tomato_mosaic_virus"
    elif preds==9:
        preds="The Disease is Tomato___healthy"
    return preds


@app.route('/', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        preds = model_predict(file_path, model)
        result=preds
        return result
    return None

@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email=request.form['email']
        user=request.form['username']
        pas=request.form['password']
        conn=sqlite3.connect('instance/users.db')
        con=conn.cursor()
        stat=f"SELECT * FROM members WHERE username='{user}' or email='{email}'"
        con.execute(stat)
        if con.fetchone():
            return render_template('signup.html', err=True)
        hashed_pas=bcrypt.generate_password_hash(pas)
        e=Members(email=email, username=user, password=hashed_pas)
        db.session.add(e)
        db.session.commit()
        entry=Members.query.all()
        print('Abc')
        return render_template('index.html', entry=entry)
    return render_template('signup.html')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route('/loginval', methods=['GET', 'POST'])
def logcheck():
    ac=request.form['ans']
    pas=request.form['password']
    # check=bcrypt.generate_password_hash(pas)
    conn=sqlite3.connect('instance/users.db')
    con=conn.cursor()
    err=False
    stat=f"SELECT * FROM members WHERE username='{ac}'"
    con.execute(stat)
    if con.fetchone():
        stat=f"SELECT password FROM members WHERE username='{ac}'"
        con.execute(stat)
        if bcrypt.check_password_hash(con.fetchone()[0], pas):
            return render_template('index.html')
        else:
            err=True
    else:
        err=True
    return render_template('login.html', err=err)

# @app.route('/home.html')
# def home():
#     return render_template('home.html')

if __name__ == '__main__':
    app.run(port=5001,debug=True)
