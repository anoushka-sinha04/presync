import sqlite3
def init_admin_db():
    conn = sqlite3.connect('admin_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
init_admin_db()


import cv2
import os
from flask import Flask,request,render_template,redirect,session,url_for
from datetime import date
from datetime import datetime
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd
import joblib
import time
# import db

#VARIABLES
MESSAGE = "WELCOME  " \
          " Instruction: to register your attendence kindly click on 'a' on keyboard"

#### Defining Flask App
app = Flask(__name__)

#### Saving Date today in 2 different formats
datetoday = date.today().strftime("%m_%d_%y")
datetoday2 = date.today().strftime("%d-%B-%Y")

#### Initializing VideoCapture object to access WebCam
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
try:
    cap = cv2.VideoCapture(1)
except:
    cap = cv2.VideoCapture(0)

#### If these directories don't exist, create them
if not os.path.isdir('Attendance'):
    os.makedirs('Attendance')
if not os.path.isdir('static'):
    os.makedirs('static')
if not os.path.isdir('static/faces'):
    os.makedirs('static/faces')
if f'Attendance-{datetoday}.csv' not in os.listdir('Attendance'):
    with open(f'Attendance/Attendance-{datetoday}.csv','w') as f:
        f.write('Name,Roll,Time')

#### get a number of total registered users

def totalreg():
    return len(os.listdir('static/faces'))

#### extract the face from an image
def extract_faces(img):
    if img!=[]:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_points = face_detector.detectMultiScale(gray, 1.3, 5)
        return face_points
    else:
        return []

#### Identify face using ML model
def identify_face(facearray):
    model = joblib.load('static/face_recognition_model.pkl')
    return model.predict(facearray)

#### A function which trains the model on all the faces available in faces folder
def train_model():
    faces = []
    labels = []
    userlist = os.listdir('static/faces')
    for user in userlist:
        for imgname in os.listdir(f'static/faces/{user}'):
            img = cv2.imread(f'static/faces/{user}/{imgname}')
            resized_face = cv2.resize(img, (50, 50))
            faces.append(resized_face.ravel())
            labels.append(user)
    faces = np.array(faces)
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(faces,labels)
    joblib.dump(knn,'static/face_recognition_model.pkl')

#### Extract info from today's attendance file in attendance folder
def extract_attendance():
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    names = df['Name']
    rolls = df['Roll']
    times = df['Time']
    l = len(df)
    return names,rolls,times,l

#### Add Attendance of a specific user
def add_attendance(name):
    username = name.split('_')[0]
    userid = name.split('_')[1]
    current_time = datetime.now().strftime("%H:%M:%S")
    
    df = pd.read_csv(f'Attendance/Attendance-{datetoday}.csv')
    if str(userid) not in list(df['Roll']):
        with open(f'Attendance/Attendance-{datetoday}.csv','a') as f:
            f.write(f'\n{username},{userid},{current_time}')
    else:
        print("this user has already marked attendence for the day , but still i am marking it ")
        # with open(f'Attendance/Attendance-{datetoday}.csv','a') as f:
        #     f.write(f'\n{username},{userid},{current_time}')


################## HELPER FUNCTIONS FOR TEMPLATES ##################

def render_home_page(mess=None):
    if mess is None:
        mess = MESSAGE
    
    # Extract attendance list safely
    names, rolls, times, l = extract_attendance()
    attendance_data = []
    for i in range(l):
        attendance_data.append({
            'name': names.iloc[i] if hasattr(names, 'iloc') else names[i],
            'id': rolls.iloc[i] if hasattr(rolls, 'iloc') else rolls[i],
            'time': times.iloc[i] if hasattr(times, 'iloc') else times[i]
        })
    
    # Extract registered users list safely from folders
    users = []
    if os.path.exists('static/faces'):
        for folder in os.listdir('static/faces'):
            if '_' in folder:
                parts = folder.split('_', 1)
                users.append({
                    'name': parts[0],
                    'id': parts[1]
                })
            else:
                users.append({
                    'name': folder,
                    'id': 'N/A'
                })
                
    return render_template(
        'home.html',
        attendance_data=attendance_data,
        users=users,
        totalreg=totalreg(),
        datetoday2=datetoday2,
        mess=mess
    )

################## ROUTING FUNCTIONS ##############################

#### Our main page
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('admin_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM admins WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()
        conn.close()
        if result:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('adminlogin.html')


@app.route('/sign')
def sign_up():
    return render_template('sign.html')

@app.route('/admin')
def admin_dashboard():
    # Make stats dynamic based on database & today's CSV file
    names, rolls, times, l = extract_attendance()
    return render_template('admin.html', total_users=totalreg(), today_attendance=l)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('admin_data.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. Try another."
        conn.close()
        return redirect(url_for('adminlogin'))
    return render_template('sign.html')

@app.route('/')
def home():
    return render_home_page()

#### This function will run when we click on Take Attendance Button
@app.route('/start',methods=['GET'])
def start():
    if 'face_recognition_model.pkl' not in os.listdir('static'):
        mess = 'This face is not registered with us , kindly register yourself first'
        print("face not in database, need to register")
        return render_home_page(mess=mess)

    cap = cv2.VideoCapture(0)
    ret = True
    ATTENDENCE_MARKED = False
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the grayscale frame
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        # Draw rectangles around the detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            face = cv2.resize(frame[y:y+h,x:x+w], (50, 50))
            identified_person = identify_face(face.reshape(1,-1))[0]
            cv2.putText(frame, f'{identified_person}', (x + 6, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 20), 2)
            if cv2.waitKey(1) == ord('a'):
                add_attendance(identified_person)
                current_time_ = datetime.now().strftime("%H:%M:%S")
                print(f"attendence marked for {identified_person}, at {current_time_} ")
                ATTENDENCE_MARKED = True
                break
        if ATTENDENCE_MARKED:
            break

        # Display the resulting frame
        cv2.imshow('Attendance Check, press "q" to exit', frame)
        cv2.putText(frame,'hello',(30,30),cv2.FONT_HERSHEY_COMPLEX,2,(255, 255, 255))
        
        # Wait for the user to press 'q' to quit
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    mess = 'Attendence taken successfully'
    print("attendence registered")
    return render_home_page(mess=mess)

@app.route('/add',methods=['GET','POST'])
def add():
    newusername = request.form['newusername']
    newuserid = request.form['newuserid']
    userimagefolder = 'static/faces/'+newusername+'_'+str(newuserid)
    if not os.path.isdir(userimagefolder):
        os.makedirs(userimagefolder)
    cap = cv2.VideoCapture(0)
    i,j = 0,0
    while 1:
        ret, frame = cap.read()
        if not ret:
            break
        faces = extract_faces(frame)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x, y), (x+w, y+h), (255, 0, 20), 2)
            cv2.putText(frame,f'Images Captured: {i}/50',(30,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255, 0, 20),2,cv2.LINE_AA)
            if j%10==0:
                name = newusername+'_'+str(i)+'.jpg'
                cv2.imwrite(userimagefolder+'/'+name,frame[y:y+h,x:x+w])
                i+=1
            j+=1
        if j==500:
            break
        cv2.imshow('Adding new User',frame)
        if cv2.waitKey(1)==27:
            break
    cap.release()
    cv2.destroyAllWindows()
    print('Training Model')
    train_model()
    
    if totalreg() > 0:
        return render_home_page(mess='User added Sucessfully')
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/add_user')
def add_user():
    return redirect(url_for('home'))

#### Our main function which runs the Flask App
if __name__ == '__main__':
    app.run(debug=True, port=1000)

