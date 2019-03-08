from theu import app, db

from theu.models import (
    User,
    UserSchema,
    Post,
    PostSchema,
    Verification,
    Like,
    LikeSchema,
)
from flask import request, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from theu.models import User, UserSchema, Post, PostSchema, Comment, CommentSchema
from flask import request, jsonify
from sqlalchemy import desc
import hashlib

from . import email_sender


from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)

import random

@app.route("/")
@app.route("/index")
def index():
    return "Hello, World!"


def create_verification_token(email):
    token = email + app.config["VERIFICATION_SECRET_KEY"]
    md5_hash = hashlib.md5(token.encode("utf-8")).hexdigest()
    return md5_hash

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

    # original user.password_hash is plain text, hash it before saving to DB
    user.password_hash = generate_password_hash(user.password_hash)
    db.session.add(user)
    db.session.commit()

    if app.config["VERIFICATION_ENABLED"]:
        # Create the verification
        verification = Verification()
        verification.user_id = user.id
        verification.token = create_verification_token(user.email)
        db.session.add(verification)
        db.session.commit()

        email_sender.send_email(
            from_email=user.email,
            to_email=user.email,
            subject="Please verify your email with the U",
            email_text="Please visit {}/verify?token={}".format(
                app.config["BACKEND_URL"], verification.token
            ),
        )

    return user_schema.jsonify(user), 201


@app.route("/verify", methods=["GET"])
def verify():
    token = request.args.get("token")
    if not token:
        return "No token"

    verification = Verification.query.filter_by(token=token).first()
    if not verification:
        return "Token is invalid"

    user = User.query.filter_by(id=verification.user_id).first()
    if not user:
        return "Unable to find user"

    user.is_verified = True
    db.session.commit()

    return redirect(app.config["FRONTEND_URL"], code=302)


# Creates the JWT token for an existing user
@app.route("/api/user/login", methods=["POST"])
def login():
    email = request.json.get("email", None)
    username = request.json.get("username", None)
    password = request.json.get("password", None)

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

    password_correct = check_password_hash(user.password_hash, password)
    if not user or not password_correct:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200


# Example of protected route
# Has to have http header of Authorization : bearer XXX where XXX is JWT token
@app.route("/api/protected", methods=["GET"])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/api/like/<int:post_id>", methods=["POST"])
@jwt_required
def like_post(post_id):
    current_user = get_jwt_identity()
    res = Like.query.get("%d:%d" % (current_user, post_id))
    post = Post.query.get_or_404(post_id)

    like_schema = LikeSchema()
    like, errors = like_schema.load(
        {
            "id": "%d:%d" % (current_user, post_id),
            "post_id": post_id,
            "user_id": current_user,
        }
    )

    if res is None:
        post.like_count = post.like_count + 1
        db.session.add(like)
    else:
        post.like_count = post.like_count - 1
        db.session.delete(like)

    db.session.add(post)
    db.session.commit()

    return jsonify({"like_count": post.like_count}), 200


@app.route("/api/post", methods=["POST"])
@jwt_required
def create_post():
    current_user_id = get_jwt_identity()
    print("current_user_id", current_user_id)
    post_schema = PostSchema()
    post, errors = post_schema.load(request.json)
    post.user_id = current_user_id

    post.like_count = 0
    post.view_count = random.randint(30, 100)
    post.comment_count = 0

    print("Saving to db post", post)
    if errors:
        return "Error" + str(errors)
    db.session.add(post)
    db.session.commit()
    return post_schema.jsonify(post), 201

@app.route("/api/comment", methods=["POST"])
@jwt_required
def create_comment():
    current_user_id = get_jwt_identity()

    comment_schema = CommentSchema()
    comment, errors = comment_schema.load(request.json)
    comment.user_id = current_user_id

    # increase the cound of comments for this post_id
    post_schema = PostSchema(many=False)
    post = Post.query.get_or_404(comment.post_id)
    post.comment_count += 1

    print("saving comment", comment)
    if errors:
        return "Error" + str(errors)
    db.session.add(comment)
    db.session.commit()
    return comment_schema.jsonify(comment), 201

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

    # create a list/array of all comments linked to that post_id
    comment_schema = CommentSchema(many=False)
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.id.desc())
    all_comments = []
    for row in comments:
        all_comments.append((row.user_id, row.text))

    return jsonify(
        {
            "username" : user.username,
            "post_text" : post.text,
            "post_title" : post.title,
            "like_count" : post.like_count,
            "view_count" : post.view_count,
            "comment_count" : post.comment_count,
            "all_comments" : all_comments
        }
    )
