from theu import db
from theu import app
from flask_marshmallow import Marshmallow

ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return "<User {}>".format(self.username)

class Verification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "<Verification {}>".format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text(), index=False, unique=False)
    text = db.Column(db.String(), index=False, unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    like_count = db.Column(db.Integer)
    view_count = db.Column(db.Integer)
    comment_count = db.Column(db.Integer)

    def __repr__(self):
        return "<Post {} {} {}>".format(self.title, self.text, self.user_id)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    text = db.Column(db.String(), index=False, unique=False)

    def __repr__(self):
        return "<Comment {} {} {}>".format(self.post_id, self.user_id, self.text)

class Like(db.Model):
    id = db.Column(db.String(), primary_key=True)
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

    def __repr__(self):
        return  "<Like {}:{}>".format(self.user_id, self.post_id)

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User

class PostSchema(ma.ModelSchema):
    class Meta:
        model = Post

class LikeSchema(ma.ModelSchema):
    class Meta:
        model = Like

if __name__ == '__main__':
    db.create_all()
    db.session.commit()

class CommentSchema(ma.ModelSchema):
    class Meta:
        model = Comment
