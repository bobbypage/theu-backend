import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL"
    ) or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "super-secret"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    BACKEND_URL = os.environ.get("BACKEND_URL") or "http://127.0.0.1:5000"
    FRONTEND_URL = os.environ.get("FRONTEND_URL") or "http://127.0.0.1:3000"
    VERIFICATION_SECRET_KEY = os.environ.get("VERIFICATION_SECRET_KEY") or "secret-verification"
    VERIFICATION_ENABLED = True if os.environ.get("VERIFICATION_ENABLED") else False

