from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

#init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Init DB
db = SQLAlchemy(app)

#init ma
ma = Marshmallow(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True) 
  username = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(20), nullable=False)

class Projects(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  description = db.Column(db.String(80), nullable=False )
  completed = db.Column(db.Boolean)
  actions = db.relationship('Actions', backref='project')

class Actions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  # check up o the foriegnkey thing
  project_id = db.Column(db.Integer,  db.ForeignKey('projects.id'), nullable=False)
  description = db.Column(db.String, nullable=False)
  note = db.Column(db.String(120), nullable=False)
 

#Run server
if __name__ == '__main__':
  app.run(debug=True)