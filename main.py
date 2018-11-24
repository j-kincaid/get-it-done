from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashUtils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:greenenchiladas@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# The secret key sets security. It can be a random string.
app.secret_key = 'nGl3C5fQyD45'

# (flask-env) $ python
# from main import db, Task
# db.create_all()
# db.session.commit()

class Task(db.Model): # We added a new column:

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean, default = False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Links to the user table

    def __init__(self, name, owner): 
        self.name = name
        self.completed = False
        self.owner = owner # Every owner is a user object
        
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True) # User objects will be 
    # unique. Every user gets a password
    pw_hash = db.Column(db.String(120))
    tasks = db.relationship('Task', backref='owner')
    # SQLAlchemy should populate the task class according to things specific to each user.

    # A constructor for the User class 
    def __init__(self, email, password):
        self.email = email
        self.pw_hash = make_pw_hash(password)

    # Generate the User table in SQLAlchemy.
    # Initiate the database while in the python shell
    # by adding a user like this:
    #
    # >>> new_user = User('4j.kincaid', 'petunia')
    # >>> db.session.commit()


@app.before_request #Check for the user's email
def require_login():
    allowed_routes = [ 'login', 'register']
    print(session)
    if request.endpoint not in allowed_routes and 'email' not in session: # If the user's not logged in, or registered, return them to the login page. 
        return redirect('/login') # We only let them past if there is a value set for the session in email. 


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': # Check for the request type
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() # We can retieve the # user with a given email if they exist
        if user and check_pw_hash(password, user.pw_hash):
            # The session is an object dictionary that "remembers" that the user has logged in
            session['email'] = email
            flash("Logged in") # Message goes in a queue to go in base.html
            print(session)
            return redirect('/') # If we're not rendering a template the flash message uses the session object to store the message for the next time the user comes back. 
        else:
            # TODO - explain why login failed
            flash('User password incorrect, or user does not exist', 'error'), 

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
            # TODO - remember the user
            session['email'] = email # sessions allow you to store an entry in the framework as a key:value pair. If they're not logged in, we redirect them to the login page as above in require_login()
            return redirect('/')
        else:
            # TODO - better response message
            return "<h1>Duplicate User</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email'] # When they log out, we take their email out of the session.
    return redirect('/')

@app.route('/', methods=['POST', 'GET'])
def index():

###################_______________##################
#### Where the new task (or new blog post) is created 
###################_______________##################


    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name, owner) # Create a new task object
        db.session.add(new_task)
        db.session.commit() # commit it to the db

    tasks = Task.query.filter_by(completed=False, owner=owner).all() 
    # only give me the tasks for which the completed column has the value False
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