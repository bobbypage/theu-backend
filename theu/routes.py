from theu import app, db

from theu.models import User, UserSchema, Post, PostSchema
from flask import request, jsonify

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)


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
    password = request.json.get('password', None)

    user = User.query.filter_by(email=email).first()
    # TODO: hash the password, don't wanna be the next experian lol
    if user.email != email or user.password_hash != password:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=email)

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
