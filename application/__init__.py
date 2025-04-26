from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
import os

# Get the base directory of the project
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Correct static and template folders
app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, 'static'),
    template_folder=os.path.join(base_dir, 'templates'),
    static_url_path='/static',
)

# Configurations
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(base_dir, 'instance', 'scrape.db')}"
app.config["SECRET_KEY"] = os.getenv("SCRAPE_SCOUT_SECRET_KEY", "default_secret_key")

# Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
csrf.init_app(app)
migrate = Migrate(app, db)

# Import routes and models after app + db are initialized
from application import routes, models
