from flask import Flask
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_share import Share
from flask_avatars import Avatars

app = Flask(__name__)
app.config['SECRET_KEY'] = '760e2033fe2af98da7c5971ca7adf726'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:nodywelete1@localhost/vedratdb"
db = SQLAlchemy(app)
share = Share(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'
login_manager.login_message_category = 'info'
avatars = Avatars(app)


#connection to google mail server
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'vedrat@gmail.com'
# app.config['MAIL_PASSWORD'] = 'pnwcnzahudmlszbe'
# app.config['MAIL_DEFAULT_SENDER'] = 'noreply@orientgoldmines.com'
# mail = Mail(app)

from vedrat import routes