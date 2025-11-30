from models.connection import db
from datetime import datetime
from flask_login import UserMixin
from models.connection import db
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import secrets




user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

# api_keys = db.Table(
#     'api_keys',
#     db.Column('id', db.Integer, primary_key=True),
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('value', db.String(128), unique=True, nullable=False),
#     db.Column('created_at', db.DateTime, default=datetime.utcnow)
# )


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    # attributo users definito in relazione dentro l'oggetto User
    def __repr__(self):
        return f'<Role {self.name}>'

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120), nullable=False)
#     body = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

#     # Relazione tra User e Post
#     user = db.relationship('User', backref=db.backref('posts', lazy=True))

#     # TODO to_dict(self)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))  # Campo per la password criptata
    create_ts = db.Column(db.DateTime, default=datetime.now())

    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))
    # api_keys = db.relationship('ApiKey', back_populates='user', lazy='dynamic')
    # @property
    # def roles(self):
    #     # TODO: query in UserRoles e poi in Roles
    #     pass

    def __str__(self):
        return f'<User id:{self.id} username: {self.username} email: {self.email}>'

    def to_dict(self):
        data = {
            'id' : self.id,
            'username' : self.username,
            'email' : self.email,
            'create_ts' : str(self.create_ts)
        }
        return data

    def set_password(self, password):
        """Imposta la password criptata."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica se la password è corretta."""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
    def __repr__(self):
        return f'<User username:{self.username}, email:{self.email}>'
    
    # def generate_api_key(mapper, connection, target):
    #     """Genera una nuova API key sicura e la salva nel DB."""
    #     key = secrets.token_hex(32) 
    #     new_key = ApiKey(user=target, value=key)
    #     db.session.add(new_key)
    #     db.session.commit()
    #     return key 

    # def get_api_keys(self):
    #     """Restituisce la lista delle chiavi API dell'utente."""
    #     return self.api_keys.all()

    # def delete_api_key(self, key_value):
    #     key = self.api_keys.filter_by(value=key_value).first()
    #     if key:
    #         db.session.delete(key)
    #         db.session.commit()
    #         return True
    #     return False

# class ApiKey(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     value = db.Column(db.String(128), unique=True, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     user = db.relationship("User", back_populates="api_keys")

#     def __repr__(self):
#         return f"<ApiKey user:{self.user_id} value:{self.value}>"

def init_db():  #nuovo stile
    # Verifica se i ruoli esistono già
    if not db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first():
        admin_role = Role(name='admin')
        db.session.add(admin_role)
        db.session.commit()

    if not db.session.execute(db.select(Role).filter_by(name='user')).scalars().first():
        user_role = Role(name='user')
        db.session.add(user_role)
        db.session.commit()

    # Verifica se l'utente admin esiste già
    if not db.session.execute(db.select(User).filter_by(username='admin')).scalars().first():
        admin_user = User(username="admin", email="admin@example.com")
        admin_user.set_password(os.getenv('ADMIN_PASSWORD'))
        
        # Aggiunge il ruolo 'admin' all'utente
        admin_role = db.session.execute(db.select(Role).filter_by(name='admin')).scalars().first()
        admin_user.roles.append(admin_role)

        db.session.add(admin_user)
        db.session.commit()
        # admin_user.generate_api_key()


