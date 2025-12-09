from flask import Flask, render_template, request, redirect, url_for, session,Response
from pymongo import MongoClient
from werkzeug.security import check_password_hash
import os
from camera_feed import generate_frames
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'mysecretkey')

# --- MongoDB Setup ---
client = MongoClient("mongodb://localhost:27017")
db = client['attendace_db']
teachers_col = db['Teachers']
classes_col = db['Classes']

attendance_col = db['Markattendance'] 
# --- Routes ---

@app.route('/')
def home():
    return render_template('login.html') 

from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    print(f"Attempting login for user: {username}")
    teacher = teachers_col.find_one({'username': username})
    print(f"Fetched teacher from DB: {teacher}")
    
    if teacher and check_password_hash(teacher['password'], password):
        session['teacher_name'] = teacher['name']
        print(f"Login successful for user: {username}")
        return redirect(url_for('dashboard'))
    else:
        print("Invalid credentials")
        return "<h3 style='color:red;text-align:center;'>Invalid credentials. Please try again.</h3>"



@app.route('/dashboard')
def dashboard():
    if 'teacher_name' not in session:
        return redirect(url_for('home'))

    teacher_name = session['teacher_name']

    # Fetch all classes from MongoDB (no filter)
    classes = list(db.Classes.find())
    for cls in classes:
        cls['_id_str'] = str(cls['_id'])
    print(f"Classes fetched for dashboard")

    return render_template('dashboard.html', classes=classes, teacher_name=teacher_name)
@app.route('/live_attendance/<class_id>')
def live_attendance(class_id):
    """Render the live attendance page for a given class"""
    if 'teacher_name' not in session:
        return redirect(url_for('home'))

    class_doc = classes_col.find_one({'_id': ObjectId(class_id)})
    if not class_doc:
        return "Class not found", 404

    # Convert ObjectId for HTML usage
    class_doc['_id_str'] = str(class_doc['_id'])

    print(f"Starting live attendance for class: {class_doc['class_name']}")
    return render_template('live_attendance.html', class_doc=class_doc)

@app.route('/video_feed')
def video_feed():
    class_id = request.args.get('class_id')
    cls = classes_col.find_one({"_id": ObjectId(class_id)})
    if not cls:
        return "Class not found", 404

    return Response(generate_frames(cls),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/logout')
def logout():
    session.pop('teacher_name', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print("App crashed:", e)

