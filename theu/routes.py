from theu import app, db

from theu.models import User, UserSchema, Post, PostSchema
from flask import request


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


@app.route("/api/user/<int:user_id>", methods=["GET"])
def route_user_id(user_id):
    user_schema = UserSchema()
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user)


@app.route("/api/user", methods=["POST"])
def create_user():
    user_schema = UserSchema()
    user, errors = user_schema.load(request.json)
    if errors:
        return "Error" + str(errors)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 201


@app.route("/api/post", methods=["POST"])
def create_post():
    post_schema = PostSchema()
    post, errors = post_schema.load(request.json)
    if errors:
        return "Error" + str(errors)
    db.session.add(post)
    db.session.commit()
    return post_schema.jsonify(post), 201


@app.route("/api/post", methods=["GET"])
def get_all_posts():
    posts_schema = PostSchema(many=True)
    all_posts = Post.query.all()
    return posts_schema.jsonify(all_posts)
