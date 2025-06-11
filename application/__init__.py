import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

# 1. Create the app & load config
app = Flask(
    __name__,
    static_folder="../static",
    template_folder="../templates",
    static_url_path="/static",
)

# ——————————————————————————————
# Pull the Postgres URL from the env and error if missing
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL environment variable not set")
app.config["SQLALCHEMY_DATABASE_URI"] = database_url

# Turn off track modifications (recommended)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Secret Key
app.config["SECRET_KEY"] = os.getenv("SCRAPE_SCOUT_SECRET_KEY", "default_secret")
# ——————————————————————————————

# 2. Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
migrate = Migrate(app, db)

# 3. Register your CLI command
from application.manage import scrape_command
app.cli.add_command(scrape_command)

# 4. Start the scheduler
from application.scheduler import start_scheduler
start_scheduler(app)

# 5. Import routes & models (they rely on app & db)
from application import routes, models
