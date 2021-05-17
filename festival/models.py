from festival import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60),nullable=False)
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_info = db.Column(db.JSON)
    

    def __repr__(self):
        return f"User('{self.username}', '{self.email}'"

class Performers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    artist_name = db.Column(db.String(100),nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    stop_time = db.Column(db.Integer, nullable=False)
    length = db.Column(db.Integer,nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Performers('{self.artist_name}', '{self.start_time}', '{self.stop_time}', '{self.stage_name}'"
