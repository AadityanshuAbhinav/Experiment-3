import os
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import get_flashed_messages
from flask_sqlalchemy import SQLAlchemy

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3") 
app.secret_key = 'your_secret_key'  # Set your secret key
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer,   db.ForeignKey("student.student_id"), nullable=False)
    ecourse_id = db.Column(db.Integer,  db.ForeignKey("course.course_id"), nullable=False)
    course = db.relationship('Course') 


# @app.route("/", methods=["GET", "POST"])
# def students():
#     if request.method == "GET":
#         #student = db.session.query(Student).all()
#         students = Student.query.all()
#         return render_template("index.html", students=students)

@app.route('/')
def student_details():
    students = Student.query.all()
    return render_template('index.html', students=students)

@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        courses = request.form.getlist('courses')

        # Check if the roll number already exists
        existing_student = Student.query.filter_by(roll_number=roll_number).first()
        if existing_student:
            flash('Roll number already exists. Please choose a different one.')
            return redirect(url_for('student_details'))

        student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
        db.session.add(student)

        for course_code in courses:
            course = Course.query.filter_by(course_code=course_code).first()
            if course:
                enrollment = Enrollments(estudent_id=student.student_id, ecourse_id=course.course_id)
                db.session.add(enrollment)

        db.session.commit()
        flash('Student added successfully')
        return redirect(url_for('student_details'))
    
    courses = Course.query.all()
    return render_template('create_student.html', courses=courses)

@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get(student_id)
    courses = Course.query.all()
    
    if not student:
        flash('Student not found')
        return redirect(url_for('student_details'))
    
    if request.method == 'POST':
        # Update student details
        student.first_name = request.form['f_name']
        student.last_name = request.form['l_name']
        db.session.commit()
        
        # Handle course enrollments
        selected_courses = request.form.getlist('courses')
        enrolled_courses = Enrollments.query.filter_by(estudent_id=student.student_id).all()
        
        for enrollment in enrolled_courses:
            if enrollment.course.course_code in selected_courses:
                selected_courses.remove(enrollment.course.course_code)
            else:
                db.session.delete(enrollment)
        
        for course_code in selected_courses:
            course = Course.query.filter_by(course_code=course_code).first()
            if course:
                enrollment = Enrollments(estudent_id=student.student_id, ecourse_id=course.course_id)
                db.session.add(enrollment)
        
        db.session.commit()
        flash('Student updated successfully')
        return redirect(url_for('student_details'))
    
    return render_template('update_student.html', student=student, courses=courses)

@app.route('/student/<int:student_id>/delete', methods=['GET'])
def delete_student(student_id):
    student = Student.query.get(student_id)
    
    if student:
        # Delete the student and associated enrollments
        enrollments = Enrollments.query.filter_by(estudent_id=student.student_id).all()
        
        for enrollment in enrollments:
            db.session.delete(enrollment)
        
        db.session.delete(student)
        db.session.commit()
        flash('Student deleted successfully')
    else:
        flash('Student not found')
    
    return redirect(url_for('student_details'))

@app.route('/student/<int:student_id>', methods=['GET'])
def view_student(student_id):
    student = Student.query.get(student_id)
    
    if student:
        enrollments = Enrollments.query.filter_by(estudent_id=student.student_id).all()
        return render_template('view_student.html', student=student, enrollments=enrollments)
    else:
        flash('Student not found')
        return redirect(url_for('student_details'))

if __name__ == '__main__':
  # Run the Flask app
  app.run()
















