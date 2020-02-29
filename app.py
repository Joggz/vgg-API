from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import os

#init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#DB
app.config['SECRET_KEY'] = 'learning'
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

  def __init__(self, username, password):
    self.username =  username
    self.password =  password

class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

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
 

#create a user

@app.route('/api/user/register', methods=['POST'])
def create_user():
  username = request.json['username']
  password = request.json['password']

  hashed_password = generate_password_hash(password, method='sha256')
  password = hashed_password
  new_user = User(username, password)

  user = user_schema.load(request.json)
  find_user = User.query.filter_by(username=user['username']).first()
  if find_user:
    raise ValidationError("username already taken, choose a different one") 

  
  db.session.add(new_user)
  db.session.commit()

  
  return user_schema.jsonify(new_user)


@app.route('/api/users/auth', methods=['POST'])
def get_auth():
  auth = request.authorization

  if not auth or not auth.username or not auth.password:
    return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!!'})

  user = User.query.filter_by(username=auth.username).first()
  
  if not user:
    return jsonify({'error' : " user doesnt exist on the database"})

  if check_password_hash(user.password, auth.password):
   token = jwt.encode({'_id' : user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])

  return jsonify({'token' : token.decode('UTF-8')})

  return make_response('Could not Verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!!'})


#Run server
if __name__ == '__main__':
  app.run(debug=True)