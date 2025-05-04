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
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///../instance/scrape.db"
)
app.config["SECRET_KEY"] = os.getenv("SCRAPE_SCOUT_SECRET_KEY", "default_secret")

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

# 5. Import routes & models (which rely on app & db)
from application import routes, models
