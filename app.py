from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# init app
app = Flask(__name__)


# Configurations
app.config['SECRET_KEY'] = 'learning'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///debian.db'  # + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB
db = SQLAlchemy(app)

# serializer
ma = Marshmallow(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True, nullable=False)
  password = db.Column(db.String(20), nullable=False)


class UserSchema(ma.Schema):
  class Meta:
    fields = ('id', 'username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class Projects(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(30), unique=True, nullable=False)
  description = db.Column(db.String(80), nullable=False)
  completed = db.Column(db.Boolean)
  # actions = db.relationship('Actions', backref=db.backref('projects', lazy=True))
  actions = db.relationship('Actions', backref='projects', lazy=True)


class ProjectSchema(ma.Schema):
  class Meta:
    fields = ('id', 'name', 'description', 'completed')


project_schema = ProjectSchema()
projects_schema = ProjectSchema(many=True)


class Actions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
  # project = db.relationship('Projects', backref=db.backref('actions', lazy=True))
  description = db.Column(db.String(120), nullable=False)
  note = db.Column(db.String(120), nullable=False)


class ActionSchema(ma.Schema):
  class Meta:
    fields = ('id', 'project_id', 'note', 'description')


action_schema = ActionSchema()
actions_schema = ActionSchema(many=True)


# create a user
# working
@app.route('/api/user/register', methods=['POST'])
def create_user():
  user = user_schema.load(request.json)
  find_user = User.query.filter_by(username=user['username']).first()

  if find_user:
    raise ValidationError("username already taken, choose a different one")

  username = user['username']
  hashed_password = generate_password_hash(user['password'], method='sha256')
  password = hashed_password

  new_user = User(username=username, password=password)

  db.session.add(new_user)
  db.session.commit()

  return user_schema.jsonify(f'welcome {username}')


@app.route('/api/users/auth', methods=['POST'])
def get_auth():
  auth = request.authorization

  if not auth or not auth.username or not auth.password:
    return make_response('Could not Verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!!'})

  user = User.query.filter_by(username=auth.username).first()

  if not user:
    return jsonify({'error': " user doesnt exist on the database"})

  if check_password_hash(user.password, auth.password):
    token = jwt.encode({'_id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])

  return jsonify({'token': token.decode('UTF-8')})

  return make_response('Could not Verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!!'})


# create project
# working
@app.route('/api/projects', methods=['POST'])
def create_project():
  project = project_schema.load(request.json)

  find_project = Projects.query.filter_by(name=project['name']).first()

  if find_project:
    raise ValidationError('project already exist...')

  name = request.json['name']
  description = request.json['description']
  completed = request.json['completed']

  new_project = Projects(name=name, description=description, completed=completed)
  db.session.add(new_project)
  db.session.commit()

  return project_schema.jsonify(new_project)


# get all projects
# working
@app.route('/api/projects', methods=['GET'])
def get_projects():
  fetch_projects = Projects.query.all()
  all_projects = projects_schema.dump(fetch_projects)
  return jsonify(all_projects)


# get single project
# working
@app.route('/api/projects/<projectid>', methods=['GET'])
def get_project(projectid):
  fetch_project = Projects.query.get(projectid)

  if not fetch_project:
    raise ValidationError('project does not exist... please add up!!!')

  return project_schema.jsonify(fetch_project)


# working
@app.route('/api/projects/<projectid>', methods=['PUT'])
def update_project(projectid):

  project = Projects.query.get(projectid)

  name = request.json['name']
  description = request.json['description']
  completed = request.json['completed']

  project.name = name
  project.description = description
  project.completed = completed

  db.session.commit()

  return project_schema.jsonify(project)


# update completed column
# working
@app.route('/api/projects/<int:projectid>', methods=['PATCH'])
def update_profile(projectid):
  project = Projects.query.get(projectid)

  completed = request.json['completed']

  project.completed = completed

  db.session.commit()

  return project_schema.jsonify(project)


# delete a particular project
@app.route('/api/projects/<projectid>', methods=['DELETE'])
def delete_profile(projectid):
  project = Projects.query.get_or_404(projectid)

  db.session.delete(project)
  db.session.commit()

  return project_schema.jsonify(project)

# add action
# working


@app.route('/api/projects/<int:projectid>/action', methods=['POST'])
def post_action(projectid):
  find_project = Projects.query.get_or_404(projectid)

  action = action_schema.load(request.json)
  description = action['description']

  note = action['note']
  new_action = Actions(description=description, note=note, project_id=projectid)

  db.session.add(new_action)

  return action_schema.jsonify(action)



# Run server
if __name__ == '__main__':
  app.run(debug=True)
