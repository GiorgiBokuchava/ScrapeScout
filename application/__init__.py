from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///scrape.db"
app.config["SECRET_KEY"] = os.getenv("SCRAPE_SCOUT_SECRET_KEY", "default_secret_key")
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
csrf.init_app(app)

migrate = Migrate(app, db)

from application import routes, models
