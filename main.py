from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:greenenchiladas@localhost:8889/get-it-done'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Task(db.Model):
# Specify data fields that go into the class, in columns

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

# Add a constructor
    def __init__(self, name):
        self.name = name 

# def email_valid(email):
#     if not @ in email:
#         return False

#     if len(email) <= 4:
#         return False

#     if not ('.' in email):
#         return False

#     if ' ' in email:
#         return False

#     return True


tasks = []

@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task = request.form['task']
        tasks.append(task)

    return render_template('todos.html',title="Get It Done!", tasks=tasks)


if __name__ == '__main__':
app.run()