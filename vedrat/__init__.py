from flask import Flask
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_share import Share
from flask_avatars import Avatars
import os

app = Flask(__name__)
#os.environ.get('SECRET_KEY')
#os.environ.get('DATABASE_URL')
#database_url = "postgresql://postgres:nodywelete1@localhost/vedratdbs"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)
share = Share(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'users.signin'
login_manager.login_message_category = 'info'
avatars = Avatars(app)


#connection to google mail server

app.config['MAIL_SERVER'] = 'mail.vedrat.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'contact@vedrat.com'
mail = Mail(app)

from vedrat.users.routes import users
from vedrat.posts.routes import posts
from vedrat.payments.routes import payments
from vedrat.main.routes import main
from vedrat.admin.routes import admin
from vedrat.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(payments)
app.register_blueprint(main)
app.register_blueprint(admin)
app.register_blueprint(errors)
