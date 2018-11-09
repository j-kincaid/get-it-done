from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:greenenchiladas@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# (flask-env) $ python
# from main import db, Blog
# db.create_all()
# db.session.commit()

class Task(db.Model): # We added a new column:

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean, default = False)

    def __init__(self, name):
        self.name = name
        self.completed = False

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # TODO - "remember" that the user has logged in
            return redirect('/')
        else:
            # TODO - explain why login failed
            return '<h1>Error!</h1>'

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST': # Create a new user, looking at register.html
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
        else:
            # TODO - better response message
            return "<h1>User already exists</h1>"


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name) # Create a new task object
        db.session.add(new_task)
        db.session.commit() # commit it to the db

    tasks = Task.query.filter_by(completed=False).all() 
    # only give me the tasks for which the completed columnhas the value False
    completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('todos.html',title="Get It Done!", tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete-task', methods=['POST'])
# Take the given task id that's posted through the form and delete it from the db
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id) # gets the specific task object by numeric id from the db

    task.completed = True
    db.session.add(task)
    db.session.commit()
    # db.session.delete(task)
    # db.session.commit()

    return redirect('/') # redirect back to the main.py


if __name__ == '__main__':
    app.run()