from flask_login import UserMixin
from __init__ import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    courses = db.relationship('Course', backref='user')

    def __repr__(self):
        return f'<Usuario {self.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    students = db.relationship('Student', backref='user')
    users_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Curso {self.name}>'

class Frequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(100))
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))

    def __repr__(self):
        return f'<Frequencia {self.id}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    num_mat = db.Column(db.Integer)
    hash_mat = db.Column(db.String(100))
    frequencies = db.relationship('Frequency', backref='student')
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __repr__(self):
        return f'<Aluno {self.name} - {self.num_mat}>'