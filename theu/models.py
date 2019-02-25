from theu import db
from theu import app
from flask_marshmallow import Marshmallow

ma = Marshmallow(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return "<User {}>".format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), index=False, unique=False)
    text = db.Column(db.String(), index=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Post {} {} {}>".format(self.title, self.text, self.user_id)


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User


class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post
