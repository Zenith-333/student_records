from flask import Flask, jsonify, request, render_template_string, redirect, url_for

app = Flask(__name__)

# ─────────────────────────────────────────────
#  In-memory student data
# ─────────────────────────────────────────────
students = [
    {"id": 1, "name": "Juan Dela Cruz",  "grade": 88, "section": "Stallman"},
    {"id": 2, "name": "Maria Santos",    "grade": 92, "section": "Stallman"},
    {"id": 3, "name": "Pedro Reyes",     "grade": 68, "section": "Zion"},
    {"id": 4, "name": "Ana Gonzales",    "grade": 75, "section": "Zion"},
    {"id": 5, "name": "Carlos Mendoza",  "grade": 55, "section": "Zechariah"},
]

def next_id():
    return max((s["id"] for s in students), default=0) + 1

def get_remarks(grade):
    return "Pass" if grade >= 75 else "Fail"

# ─────────────────────────────────────────────
#  HTML Templates
# ─────────────────────────────────────────────
BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Student Grade API</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #f0f4f8; color: #2d3748; }
    header { background: #4f46e5; color: white; padding: 1rem 2rem;
             display: flex; align-items: center; gap: 1rem; }
    header h1 { font-size: 1.4rem; }
    nav a { color: #c7d2fe; text-decoration: none; margin-right: 1.2rem;
            font-size: 0.9rem; }
    nav a:hover { color: white; }
    .container { max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
    .card { background: white; border-radius: 10px; padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,.08); margin-bottom: 1.5rem; }
    h2 { font-size: 1.2rem; margin-bottom: 1rem; color: #4f46e5; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #4f46e5; color: white; padding: .6rem 1rem; text-align: left; }
    td { padding: .6rem 1rem; border-bottom: 1px solid #e2e8f0; }
    tr:hover td { background: #f7f8ff; }
    .badge { padding: .2rem .6rem; border-radius: 20px; font-size: .8rem; font-weight: 600; }
    .pass { background: #d1fae5; color: #065f46; }
    .fail { background: #fee2e2; color: #991b1b; }
    a.btn, button { display: inline-block; padding: .45rem 1rem; border-radius: 6px;
                    text-decoration: none; font-size: .85rem; cursor: pointer;
                    border: none; transition: opacity .2s; }
    a.btn:hover, button:hover { opacity: .85; }
    .btn-primary { background: #4f46e5; color: white; }
    .btn-warn    { background: #f59e0b; color: white; }
    .btn-danger  { background: #ef4444; color: white; }
    .btn-gray    { background: #94a3b8; color: white; }
    form label { display: block; margin-bottom: .3rem; font-size: .9rem; font-weight: 500; }
    form input, form select { width: 100%; padding: .5rem; border: 1px solid #cbd5e1;
                              border-radius: 6px; margin-bottom: 1rem; font-size: .95rem; }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px,1fr));
                 gap: 1rem; }
    .stat-box { text-align: center; padding: 1rem; border-radius: 8px; }
    .stat-box .val { font-size: 2rem; font-weight: 700; }
    .stat-box .lbl { font-size: .8rem; margin-top: .3rem; }
    .s-blue   { background:#e0e7ff; color:#3730a3; }
    .s-green  { background:#d1fae5; color:#065f46; }
    .s-red    { background:#fee2e2; color:#991b1b; }
    .s-yellow { background:#fef9c3; color:#854d0e; }
    .alert-success { background:#d1fae5; color:#065f46; padding:.8rem 1rem;
                     border-radius:6px; margin-bottom:1rem; }
    .api-table td:first-child { font-family: monospace; font-size:.85rem; color:#6366f1; }
  </style>
</head>
<body>
<header>
  <div>
    <h1>🎓 Student Grade API</h1>
    <nav>
      <a href="/">Home</a>
      <a href="/students">Students</a>
      <a href="/add_student_form">Add Student</a>
      <a href="/summary">Summary (JSON)</a>
      <a href="/students_json">All Students (JSON)</a>
    </nav>
  </div>
</header>
<div class="container">
  {% block content %}{% endblock %}
</div>
</body>
</html>
"""

HOME_TMPL = BASE.replace("{% block content %}{% endblock %}", """
<div class="card">
  <h2>Welcome to the Student Grade API</h2>
  <p style="margin-bottom:1rem;color:#64748b;">
    A full CRUD Flask API with grade evaluation, analytics, and validation.
  </p>
  <div class="stat-grid" style="margin-bottom:1.5rem;">
    <div class="stat-box s-blue"><div class="val">{{ total }}</div><div class="lbl">Total Students</div></div>
    <div class="stat-box s-green"><div class="val">{{ passed }}</div><div class="lbl">Passed</div></div>
    <div class="stat-box s-red"><div class="val">{{ failed }}</div><div class="lbl">Failed</div></div>
    <div class="stat-box s-yellow"><div class="val">{{ avg }}</div><div class="lbl">Avg Grade</div></div>
  </div>
  <a class="btn btn-primary" href="/students">View All Students</a>
  <a class="btn btn-gray" href="/add_student_form" style="margin-left:.5rem;">+ Add Student</a>
</div>

<div class="card">
  <h2>API Endpoints</h2>
  <table class="api-table">
    <tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>
    <tr><td>GET</td><td>/students_json</td><td>Return all students as JSON</td></tr>
    <tr><td>GET</td><td>/student/&lt;id&gt;</td><td>Return a single student by ID</td></tr>
    <tr><td>POST</td><td>/add_student</td><td>Add a new student</td></tr>
    <tr><td>POST</td><td>/update_student/&lt;id&gt;</td><td>Update student data</td></tr>
    <tr><td>DELETE</td><td>/delete_student/&lt;id&gt;</td><td>Delete a student</td></tr>
    <tr><td>GET</td><td>/summary</td><td>Grade analytics (JSON)</td></tr>
    <tr><td>GET</td><td>/student?grade=85</td><td>Quick grade check (JSON)</td></tr>
  </table>
</div>
""")

LIST_TMPL = BASE.replace("{% block content %}{% endblock %}", """
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
    <h2>Student List</h2>
    <a class="btn btn-primary" href="/add_student_form">+ Add Student</a>
  </div>
  {% if msg %}<div class="alert-success">{{ msg }}</div>{% endif %}
  <table>
    <tr>
      <th>ID</th><th>Name</th><th>Section</th><th>Grade</th><th>Remarks</th><th>Actions</th>
    </tr>
    {% for s in students %}
    <tr>
      <td>{{ s.id }}</td>
      <td>{{ s.name }}</td>
      <td>{{ s.section }}</td>
      <td>{{ s.grade }}</td>
      <td><span class="badge {{ 'pass' if s.grade >= 75 else 'fail' }}">
          {{ 'Pass' if s.grade >= 75 else 'Fail' }}</span></td>
      <td>
        <a class="btn btn-warn" href="/edit_student/{{ s.id }}">Edit</a>
        <a class="btn btn-danger" href="/confirm_delete/{{ s.id }}"
           style="margin-left:.3rem;">Delete</a>
      </td>
    </tr>
    {% endfor %}
  </table>
</div>
""")

ADD_TMPL = BASE.replace("{% block content %}{% endblock %}", """
<div class="card" style="max-width:480px;">
  <h2>Add New Student</h2>
  {% if error %}<div style="color:#ef4444;margin-bottom:.8rem;">⚠ {{ error }}</div>{% endif %}
  <form action="/add_student" method="POST">
    <label>Full Name</label>
    <input type="text" name="name" placeholder="e.g. Juan Dela Cruz" required autofocus>
    <label>Grade (0–100)</label>
    <input type="number" name="grade" min="0" max="100" placeholder="e.g. 85" required>
    <label>Section</label>
    <input type="text" name="section" placeholder="e.g. Stallman" required>
    <button type="submit" class="btn btn-primary">Add Student</button>
    <a class="btn btn-gray" href="/students" style="margin-left:.5rem;">Cancel</a>
  </form>
</div>
""")

EDIT_TMPL = BASE.replace("{% block content %}{% endblock %}", """
<div class="card" style="max-width:480px;">
  <h2>Edit Student #{{ student.id }}</h2>
  {% if error %}<div style="color:#ef4444;margin-bottom:.8rem;">⚠ {{ error }}</div>{% endif %}
  <form action="/update_student/{{ student.id }}" method="POST">
    <label>Full Name</label>
    <input type="text" name="name" value="{{ student.name }}" required>
    <label>Grade (0–100)</label>
    <input type="number" name="grade" value="{{ student.grade }}" min="0" max="100" required>
    <label>Section</label>
    <input type="text" name="section" value="{{ student.section }}" required>
    <button type="submit" class="btn btn-primary">Update</button>
    <a class="btn btn-gray" href="/students" style="margin-left:.5rem;">Cancel</a>
  </form>
</div>
""")

DELETE_TMPL = BASE.replace("{% block content %}{% endblock %}", """
<div class="card" style="max-width:420px;">
  <h2>Confirm Delete</h2>
  <p style="margin-bottom:1.2rem;">
    Are you sure you want to delete <strong>{{ student.name }}</strong>?
  </p>
  <form action="/delete_student/{{ student.id }}" method="POST">
    <button type="submit" class="btn btn-danger">Yes, Delete</button>
    <a class="btn btn-gray" href="/students" style="margin-left:.5rem;">Cancel</a>
  </form>
</div>
""")

# ─────────────────────────────────────────────
#  Routes – Browser UI
# ─────────────────────────────────────────────

@app.route('/')
def home():
    grades  = [s["grade"] for s in students]
    passed  = sum(1 for g in grades if g >= 75)
    failed  = len(grades) - passed
    avg     = round(sum(grades) / len(grades), 1) if grades else 0
    return render_template_string(HOME_TMPL,
        total=len(students), passed=passed, failed=failed, avg=avg)

@app.route('/students')
def list_students():
    msg = request.args.get("msg", "")
    return render_template_string(LIST_TMPL, students=students, msg=msg)

@app.route('/add_student_form')
def add_student_form():
    return render_template_string(ADD_TMPL, error="")

@app.route('/add_student', methods=['POST'])
def add_student():
    name    = request.form.get("name", "").strip()
    section = request.form.get("section", "").strip()
    raw     = request.form.get("grade", "")

    # Validation
    if not name or not section:
        return render_template_string(ADD_TMPL, error="Name and section are required.")
    try:
        grade = int(raw)
    except ValueError:
        return render_template_string(ADD_TMPL, error="Grade must be a number.")
    if not (0 <= grade <= 100):
        return render_template_string(ADD_TMPL, error="Grade must be between 0 and 100.")

    new_student = {"id": next_id(), "name": name, "grade": grade, "section": section}
    students.append(new_student)
    return redirect(url_for('list_students', msg="Student added successfully!"))

@app.route('/edit_student/<int:sid>', methods=['GET'])
def edit_student_form(sid):
    student = next((s for s in students if s["id"] == sid), None)
    if not student:
        return "Student not found", 404
    return render_template_string(EDIT_TMPL, student=student, error="")

@app.route('/update_student/<int:sid>', methods=['POST'])
def update_student(sid):
    student = next((s for s in students if s["id"] == sid), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    name    = request.form.get("name", "").strip()
    section = request.form.get("section", "").strip()
    raw     = request.form.get("grade", "")

    if not name or not section:
        return render_template_string(EDIT_TMPL, student=student,
                                      error="Name and section are required.")
    try:
        grade = int(raw)
    except ValueError:
        return render_template_string(EDIT_TMPL, student=student,
                                      error="Grade must be a number.")
    if not (0 <= grade <= 100):
        return render_template_string(EDIT_TMPL, student=student,
                                      error="Grade must be between 0 and 100.")

    student["name"]    = name
    student["grade"]   = grade
    student["section"] = section
    return redirect(url_for('list_students', msg="Student updated successfully!"))

@app.route('/confirm_delete/<int:sid>')
def confirm_delete(sid):
    student = next((s for s in students if s["id"] == sid), None)
    if not student:
        return "Student not found", 404
    return render_template_string(DELETE_TMPL, student=student)

@app.route('/delete_student/<int:sid>', methods=['POST'])
def delete_student(sid):
    global students
    original = len(students)
    students = [s for s in students if s["id"] != sid]
    if len(students) == original:
        return jsonify({"error": "Student not found"}), 404
    return redirect(url_for('list_students', msg="Student deleted successfully!"))

# ─────────────────────────────────────────────
#  Routes – JSON API
# ─────────────────────────────────────────────

@app.route('/students_json', methods=['GET'])
def get_students_json():
    enriched = [{**s, "remarks": get_remarks(s["grade"])} for s in students]
    return jsonify(enriched)

@app.route('/student/<int:sid>', methods=['GET'])
def get_student_by_id(sid):
    student = next((s for s in students if s["id"] == sid), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify({**student, "remarks": get_remarks(student["grade"])})

@app.route('/student', methods=['GET'])
def grade_check():
    """Quick grade check: /student?grade=85"""
    try:
        grade = int(request.args.get('grade', 0))
    except ValueError:
        return jsonify({"error": "Grade must be a number"}), 400
    if not (0 <= grade <= 100):
        return jsonify({"error": "Grade must be between 0 and 100"}), 400
    return jsonify({"grade": grade, "remarks": get_remarks(grade)})

@app.route('/summary', methods=['GET'])
def summary():
    if not students:
        return jsonify({"message": "No students found"})
    grades  = [s["grade"] for s in students]
    passed  = [s for s in students if s["grade"] >= 75]
    failed  = [s for s in students if s["grade"] <  75]
    return jsonify({
        "total_students" : len(students),
        "average_grade"  : round(sum(grades) / len(grades), 2),
        "highest_grade"  : max(grades),
        "lowest_grade"   : min(grades),
        "passed_count"   : len(passed),
        "failed_count"   : len(failed),
        "pass_rate"      : f"{round(len(passed)/len(students)*100, 1)}%",
        "top_student"    : max(students, key=lambda s: s["grade"])["name"],
    })

# ─────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
