from theu import app, db

from theu.models import User, UserSchema, Post, PostSchema
from flask import request, jsonify
from sqlalchemy import desc


from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
import random


@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


@app.route("/api/user/<int:user_id>", methods=["GET"])
def route_user_id(user_id):
    user_schema = UserSchema()
    user = User.query.get_or_404(user_id)
    return user_schema.jsonify(user)

# Creates a new user
@app.route("/api/user", methods=["POST"])
def create_user():
    user_schema = UserSchema()
    user, errors = user_schema.load(request.json)
    if errors:
        return "Error" + str(errors)
    db.session.add(user)
    db.session.commit()
    return user_schema.jsonify(user), 201

# Creates the JWT token for an existing user
@app.route("/api/user/login", methods=["POST"])
def login():
    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if email is None and username is None:
        return jsonify({"msg": "Provide username or email"}), 401

    if password is None:
        return jsonify({"msg": "Provide password"}), 401

    user = None

    # TODO: hash the password, don't wanna be the next experian lol
    if email is not None:
        user = User.query.filter_by(email=email).first()
    else:
        user = User.query.filter_by(username=username).first()

    if not user or user.password_hash != password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


# Example of protected route
# Has to have http header of Authorization : bearer XXX where XXX is JWT token
@app.route('/api/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/api/post", methods=["POST"])
@jwt_required
def create_post():
    current_user_id = get_jwt_identity()
    print("current_user_id", current_user_id)
    post_schema = PostSchema()
    post, errors = post_schema.load(request.json)
    post.user_id = current_user_id

    post.like_count = random.randint(10, 30)
    post.view_count = random.randint(30, 100)
    post.comment_count = random.randint(0, 5)

    print("Going to save to db post", post)
    if errors:
        return "Error" + str(errors)
    db.session.add(post)
    db.session.commit()
    return post_schema.jsonify(post), 201


@app.route("/api/post", methods=["GET"])
def get_all_posts():
    posts_schema = PostSchema(many=True)
    all_posts = Post.query.order_by(Post.id.desc()).all()
    return posts_schema.jsonify(all_posts)

@app.route("/api/post/<int:post_id>", methods=["GET"])
def get_post_by_id(post_id):
    post_schema = PostSchema(many=False)
    post = Post.query.get_or_404(post_id)

    user_schema = UserSchema(many=False)
    user = User.query.get_or_404(post.user_id)

    return jsonify(
        {
            "username" : user.username,
            "post_text" : post.text,
            "post_title" : post.title,
            "like_count" : post.like_count,
            "view_count" : post.view_count,
            "comment_count" : post.comment_count
        }
    )
