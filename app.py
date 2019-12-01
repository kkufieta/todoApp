from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import sys
from flask_migrate import Migrate


# Creates an application that's named like our file: app
app = Flask(__name__)
# Create database from terminal using: createdb todoapp
# Reset database: dropdb todoapp && createdb todoapp
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db object links SQLALchemy to our flask app
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# Add todo in python interactive mode: todo = Todo(description="Todo 1")
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description} {self.completed}>'

# Ensure that the tables are created for all the models 
# that we've declared and they haven't yet been created.
# UPDATE: since we're using migrations, we won't be using this any more!
# db.create_all()

# Set up a route that listens to our homepage
# We'll call our route index.
# Let's return an HTML template: 
# use render_template to specify an HTML file to render to the user 
# whenever our user visits this route.
@app.route('/')
def index():
    # Let's create index.html. Flask looks by default for templates in a folder
    # called templates located in our project directory.
    return render_template('index.html', data=Todo.query.order_by('id').all())

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
        body['completed'] = todo.completed
        body['id'] = todo.id
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=['post'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/todos/<todo_id>/delete', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({ 'success': True})



if __name__ == '__main__':
    app.run(debug=True)
