from flask import Flask
from flask_cors import CORS

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

app = Flask(__name__)
CORS(app)
jwt = JWTManager(app)


app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from theu import routes, models
