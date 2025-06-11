import os
from flask import Flask
from flask_migrate import Migrate
from application import app, db

# ensure SQLAlchemy picks up DATABASE_URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)

if __name__ == "__main__":
    # for local dev: python run.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
