# PreSync - Face Recognition Attendance System

**PreSync* is a cutting-edge attendance tracking system that uses webcam-based face recognition. With a sleek and user-friendly interface, it enables administrators to manage users securely and automatically record attendance through real-time face detection.

---

## 🚀 Features

- 🎥 Real-time face recognition using a webcam
- 👤 Secure admin login and sign-up system (powered by SQLite)
- ➕ Easily add new users with live face capture
- 📋 Attendance is logged with precise timestamps
- 📁 Attendance records are automatically saved in CSV format
- 🧠 Model training utilizes K-Nearest Neighbors
- 🖼️ Responsive user interface featuring a sidebar and dashboard layout
- ✅ Stylish modern UI with a custom theme (Mauve + Cream + Graphite)

---

## 🛠️ Tech Stack

- **Frontend:** HTML, CSS (custom + Bootstrap), Jinja2 (via Flask templates)
- **Backend:** Python, Flask
- **Database:** SQLite (`admin_data.db`)
- **ML:** OpenCV, scikit-learn, NumPy, Pandas, joblib

---
<pre>
## 📁 Project Structure
```
├── Attendance/                   # Daily attendance CSVs
├── static/
│   ├── faces/                    # User face image folders
│   ├── images/logo.png           # Logo image
│   ├── style.css                 # Stylesheet
├── templates/
│   ├── home.html                 # Dashboard (home)
│   ├── adminlogin.html           # Admin login page
│   ├── sign.html                 # Admin signup page
│   └── admin.html                # Admin panel
├── venv                          # Virtual environment
├── admin_data.db                 # Admin credentials database
├── app.py                        # Main Flask app
├── haarcascade_frontalface_default.xml  # Face detection model
└── README.md
```
</pre>
---

## 👤Admin Workflow

1. Sign up or log in at /adminlogin
2. Use the webcam to add users → it captures 50 face images
3. The model trains automatically
4. Start face recognition for attendance by clicking a button
5. Attendance logs are saved to a CSV file with a timestamp

---

## 📌 Notes
- To mark attendance, simply press A once the face is detected.
- You can stop the webcam capture at any time by hitting Q or Esc.
- Make sure the haarcascade_frontalface_default.xml file is in the root directory.

---

## 💡 Future Enhancements
- Allow face registration through file uploads
- Integrate a confidence threshold for face recognition
- Create a student portal where users can log in to view their own attendance

---

## 📜 License
This project is open-source and falls under the MIT License.

---

## ✨ Credits
Originally inspired by various open-source face recognition repositories.

---
