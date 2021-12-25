from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# INITIALIZES FLASK APP
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
URL = os.environ['OFFERS_URL']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
headers = {"Bearer": ACCESS_TOKEN}

from app import routes