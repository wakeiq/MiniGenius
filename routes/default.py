from flask import Blueprint
from flask import render_template

app = Blueprint('default', __name__)

# @app.route('/')
# def home():
#     return render_template('home.html')

@app.route('/about')
def about():     
    return render_template('about.html')

@app.route('/hello')
@app.route('/hello/<name>')
def hello(name='Mozzo'):
    return render_template('hello.html', name=name)

