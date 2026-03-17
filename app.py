import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Get the database URL from the environment variable (Render sets this)
# If it's not found (local development), use the local SQLite file.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "age": self.age, "grade": self.grade}

# --- Initialize Database ---
# This runs when the app starts and creates tables if they don't exist
with app.app_context():
    db.create_all()

# --- Routes ---

# 1. Homepage (Fixes the "Not Found" error)
@app.route('/')
def home():
    return jsonify({"message": "Welcome! Use /students to manage data."})

# 2. Add a Student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    new_student = Student(name=data['name'], age=data['age'], grade=data['grade'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

# 3. Get All Students
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

if __name__ == '__main__':
    app.run(debug=True)
