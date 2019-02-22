from flask import Flask
from flask_cors import CORS

from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


app = Flask(__name__)
CORS(app)

app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

from theu import routes, models
