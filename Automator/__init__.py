from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from google.auth.exceptions import TransportError
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Automator.db'
app.config["SECRET_KEY"] = 'd530dbaa89650308ce040b04'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login_page'
login_manager.login_message = ["Please sign in first", "success"]


class SavedEdits:
    edits = {}

    @classmethod
    def addEdit(cls, field, value):
        cls.edits[field] = value

    @classmethod
    def clear(cls):
        cls.edits = {}


class Authentication:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
             'https://www.googleapis.com/auth/documents']
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=scope)
    service = build('docs', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)

    @classmethod
    def refresh(cls):
        cls.scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
                 'https://www.googleapis.com/auth/documents']
        cls.credentials = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=cls.scope)
        cls.service = build('docs', 'v1', credentials=cls.credentials)
        cls.drive_service = build('drive', 'v3', credentials=cls.credentials)


class SavedInfo:
    sheet = ""
    users = []

    @classmethod
    def clear(cls):
        cls.sheet = ""

    @classmethod
    def set(cls, sheet, users):
        cls.sheet = sheet
        cls.users = users

from Automator import routes


