import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# UPDATED: Read the DATABASE_URL from the environment (Render sets this automatically)
# If it's not found (like on your local computer), use the sqlite file.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///students.db')

# This line is often needed to avoid a warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "age": self.age, "grade": self.grade}

# UPDATED: Use app.app_context() instead of before_first_request
with app.app_context():
    db.create_all()

@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    new_student = Student(name=data['name'], age=data['age'], grade=data['grade'])
    db.session.add(new_student)
    db.session.commit()
    return jsonify(new_student.to_dict()), 201

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([student.to_dict() for student in students])

if __name__ == '__main__':
    app.run(debug=True)
