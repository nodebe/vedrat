from vedrat.models import Contact, User, Post, FAQ
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

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
	name = StringField('Name <span class="text-danger">*</span>', validators=[DataRequired('Please fill in your name'),Length(min=4,max=20)])
	message = TextAreaField('Message <span class="text-danger">*</span>', validators=[DataRequired('Please fill in your message')])
	subject = StringField('Subject <span class="text-danger">*</span>', validators=[DataRequired('Please fill the subject of the message')])
	email = StringField('Email <span class="text-danger">*</span>', validators=[Email('Please fill in a valid email address')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(ContactForm, self).__init__(*args, **kwargs)

class PasswordResetForm(FlaskForm):
	email = StringField('Email', validators=[Email('Please fill in a valid email address')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PasswordResetForm, self).__init__(*args, **kwargs)

class PasswordChangeForm(FlaskForm):
	oldpassword = PasswordField('Old Password: <span class="text-danger">*</span>',
		validators=[DataRequired('Please fill in your old password')])
	newpassword = PasswordField('New Password: <span class="text-danger">*</span>',
		validators=[DataRequired('Please fill in your new password'), Length(min=6)])
	confirmnewpassword = PasswordField('Confirm Password: <span class="text-danger">*</span>',
		validators=[EqualTo('newpassword')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PasswordChangeForm, self).__init__(*args, **kwargs)