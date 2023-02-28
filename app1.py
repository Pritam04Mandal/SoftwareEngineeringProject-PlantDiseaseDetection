from flask import Flask,render_template,request,redirect,url_for,session
from werkzeug.utils import secure_filename
import os
import tensorflow as tf
import numpy as np
import sqlite3
from flask_bcrypt import Bcrypt
from PIL import Image
from rembg import remove

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



conn=sqlite3.connect('instance/user.db')
con=conn.cursor()

app = Flask(__name__)
app.secret_key = 'secret_key'
bcrypt=Bcrypt(app)

def user_exists(username):
    stat=f"SELECT * FROM members WHERE username='{username}'"
    con.execute(stat)
    if con.fetchone():
        return True
    else:
        return False

def check_password(username, password):
    stat=f"SELECT password FROM members WHERE username='{username}'"
    con.execute(stat)
    if bcrypt.check_password_hash(con.fetchone()[0], password):
        return True
    else:
        return False

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/loginval', methods=['GET', 'POST'])
def logincheck():
    if request.method == 'POST':
        # handle login request
        username = request.form['username']
        password = request.form['password']
        # check if the user exists and the password is correct
        if user_exists(username) and check_password(username, password):
            # create a session for the user
            session['username'] = username
            return redirect(url_for('index.html'))
        else:
            return render_template('login.html', err=True)
    else:
        return render_template('login.html')

def create_user(username, password, email):
    hashed_pas=bcrypt.generate_password_hash(password)
    stat=f"INSERT INTO Members VALUES (email, username, hashed_pas)"
    con.execute(stat)



@app.route('/signup.html', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # handle sign-up request
        email=request.form['email']
        username = request.form['username']
        password = request.form['password']
        # check if the user already exists
        if user_exists(username):
            return render_template('signup.html', err=True)
        else:
            # create a new user
            create_user(username, password, email)
            # create a session for the user
            session['username'] = username
            return redirect(url_for('index.html'))
    else:
        return render_template('signup.html')
    

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
        # removing the background
        inpt=Image.open(file_path)
        if(".jpg" in f.filename):
            temp=f.filename.replace(".jpg",".png")
        else:
            temp=f.filename
        new_path=os.path.join(basepath,'uploads',secure_filename(temp))
        inpt.save(new_path)
        inpt=Image.open(new_path)
        output=remove(inpt)
        """ fpp=str(file_path)
        if(".jpg" in fpp):
            print(fpp)
            fpp.replace(".jpg",".png") """
        output.save(new_path)
        # Make prediction
        preds = model_predict(new_path, model)
        result=preds
        return result
    return None

if __name__ == '__main__':
    app.run(port=5001, debug=True)