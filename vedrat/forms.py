from vedrat.models import Contact, User, Post, FAQ
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

banks = [('Access Bank','Access Bank'),('Citibank','Citibank'),('Diamond Bank','Diamond Bank'),('Dynamic Standard Bank','Dynamic Standard Bank'),('Ecobank Nigeria','Ecobank Nigeria'),('Fidelity Bank Nigeria','Fidelity Bank Nigeria'),('First Bank of Nigeria','First Bank of Nigeria'),('First City Monument Bank','First City Monument Bank'),('Guaranty Trust Bank','Guaranty Trust Bank'),('Heritage Bank Plc','Heritage Bank Plc'),('Jaiz Bank','Jaiz Bank'),('Keystone Bank Limited','Keystone Bank Limited'),('Providus Bank Plc','Providus Bank Plc'),('Polaris Bank','Polaris Bank'),('Stanbic IBTC Bank Nigeria Limited','Stanbic IBTC Bank Nigeria Limited'),('Standard Chartered Bank','Standard Chartered Bank'),('Sterling Bank','Sterling Bank'),('Suntrust Bank Nigeria Limited','Suntrust Bank Nigeria Limited'),('Union Bank of Nigeria','Union Bank of Nigeria'),('United Bank for Africa','United Bank for Africa'),('Unity Bank Plc','Unity Bank Plc'),('Wema Bank','Wema Bank'),('Zenith Bank','Zenith Bank')]

class UserRegForm(FlaskForm):
	fullname = StringField('', validators=[DataRequired('Please fill in a username'), Length(min=3,max=30)])
	email = StringField('', validators=[Email('Please fill in a valid email address')])
	password = PasswordField('', validators=[DataRequired('Please choose a strong password'), Length(min=6)])
	confirm = PasswordField('', validators=[EqualTo('password')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(UserRegForm, self).__init__(*args, **kwargs)

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email already exists!')

class UserLogForm(FlaskForm):
	email = StringField('',
		validators=[Email('Please fill in a valid email address')])
	password = PasswordField('',
		validators=[DataRequired('Please fill in your password')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(UserLogForm, self).__init__(*args, **kwargs)

class ContactForm(FlaskForm):
	fullname = StringField('Fullname <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your name'),Length(min=4,max=20)])
	message = TextAreaField('Message <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your message')])
	subject = SelectField('Subject <span class="text-muted">*</span>',choices=[('Making a deposit','Making a deposit'),('Making a withdrawal','Making a withdrawal'),('Posting an ad','Posting an ad'),('Login issues','Login issues'),('Signup issues','Signup issues'),('Others..','Others..') ], validators=[DataRequired('Please fill the subject of the message')])
	email = StringField('Email <span class="text-muted">*</span>', validators=[Email('Please fill in a valid email address')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(ContactForm, self).__init__(*args, **kwargs)

class PasswordResetForm(FlaskForm):
	email = StringField('Email', validators=[Email('Please fill in a valid email address')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PasswordResetForm, self).__init__(*args, **kwargs)

class PasswordChangeForm(FlaskForm):
	oldpassword = PasswordField('',
		validators=[DataRequired('Please fill in your old password')])
	newpassword = PasswordField('',
		validators=[DataRequired('Please fill in your new password'), Length(min=6)])
	confirmnewpassword = PasswordField('',
		validators=[EqualTo('newpassword')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PasswordChangeForm, self).__init__(*args, **kwargs)

class SettingsForm(FlaskForm):
	fullname = StringField('', validators=[DataRequired('Please fill in a username'), Length(min=3,max=30)])
	email = StringField('', validators=[Email('Please fill in a valid email address')])
	phone = IntegerField('')
	bank_name = SelectField('', choices=banks)
	acc_name = StringField('')
	acc_number = IntegerField('')

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(SettingsForm, self).__init__(*args, **kwargs)

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email already exists!')