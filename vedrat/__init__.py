from flask import Flask
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_share import Share
from flask_avatars import Avatars
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '760e2033fe2af98da7c5971ca7adf726'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:nodywelete1@localhost/vedratdbs"
db = SQLAlchemy(app)
share = Share(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message_category = 'info'
avatars = Avatars(app)


#connection to google mail server
#EMAIL_PASSWORD = os.environ.get('SMTP_PASSWORD')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'vedratnigeria@gmail.com'
app.config['MAIL_PASSWORD'] = 'Vedrat_nigeria1#'
app.config['MAIL_DEFAULT_SENDER'] = 'vedratnigeria@gmail.com'
mail = Mail(app)

from vedrat import routes