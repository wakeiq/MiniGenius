from flask import Flask
from flask import request
import os
from dotenv import load_dotenv
from flask import jsonify
from flask import json
from routes.default import app as bp_default
from routes.user import app as bp_user
from routes.auth import auth as bp_auth
from routes.page import page as bp_page
from models.connection import db
from flask_migrate import Migrate
from flask_login import LoginManager
from models.model import User
from models.model import init_db

app = Flask(__name__)


load_dotenv()
host = os.getenv('HOST')
port = os.getenv('PORT')

app = Flask(__name__)

app.register_blueprint(bp_default)
app.register_blueprint(bp_auth)
app.register_blueprint(bp_user, url_prefix='/user')
app.register_blueprint(bp_page)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
migrate = Migrate(app, db)

# flask_login user loader block
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()
    
    # return User.query.get(int(user_id))   # legacy
    
    return user


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)