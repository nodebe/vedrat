from vedrat import db, login_manager
from vedrat.utils import unique_id
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.String(10), nullable=False, unique=True)
	fullname = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(50), unique=True, nullable=False)
	phone = db.Column(db.String(15), default='')
	password = db.Column(db.String(120), nullable=False)
	referrer = db.Column(db.String(10), default='')
	bank_name = db.Column(db.String(90), default='')
	acc_number = db.Column(db.Integer, default=0)
	acc_name = db.Column(db.String(70), default='')
	plan = db.Column(db.String(1), default='0')
	balance = db.Column(db.Integer, default=0)
	account_status = db.Column(db.String(10), default='open')
	date_of_payment = db.Column(db.DateTime)
	ad_collected_on_day = db.Column(db.Integer, default=0)
	ad_collected_date = db.Column(db.String(12))
	can_post = db.Column(db.Integer, default=0)
	referred_plan_1 = db.Column(db.Integer, default=0)
	referred_plan_2 = db.Column(db.Integer, default=0)
	user_status = db.Column(db.String(10), nullable=False, default='member')
	
	def __repr__(self):
		return f"User('{self.fullname}','{self.password}','{self.email}','{self.phone}'')"

class Contact(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.String(20), nullable=False)
	email = db.Column(db.String(50), nullable=False)
	subject = db.Column(db.String(120), nullable=False)
	message = db.Column(db.Text, nullable=False)
	read = db.Column(db.String(1), default='0')

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.String(10), nullable=False, default=unique_id, unique=True)
	poster_id = db.Column(db.String(10), nullable=False)
	title = db.Column(db.String(50), nullable=False)
	image = db.Column(db.String(20), nullable=False)
	link = db.Column(db.Text)
	description = db.Column(db.Text, nullable=False)
	posters_needed = db.Column(db.Integer, nullable=False)
	posters_applied = db.Column(db.Integer, default=0)
	post_status = db.Column(db.String(10), default='open')
	category = db.Column(db.String(20), nullable=False)
	report = db.Column(db.Integer, default=0)

class PickedPost(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.String(10))
	post_id = db.Column(db.String(10), nullable=False)
	picker_id = db.Column(db.String(10), nullable=False)
	main_link = db.Column(db.Text, nullable=False)
	web_link = db.Column(db.String(40), nullable=False)
	description = db.Column(db.Text)
	clicks = db.Column(db.Integer, default=0)

class FAQ(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	question = db.Column(db.Text, nullable=False)
	answer = db.Column(db.Text, nullable=False)

'''class Transactiondb(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.String(10), nullable=False)
	transaction_id = db.Column(db.String, nullable=False, default=unique_id, unique=True)
	pay_for = db.Column(db.String(10), nullable=False)'''
