from vedrat.models import Contact, User, Post, FAQ
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, IntegerField, TextAreaField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, URL, NumberRange

banks = [('Access Bank', 'Access Bank'), ('Access Bank (Diamond)', 'Access Bank (Diamond)'), ('ALAT by WEMA', 'ALAT by WEMA'), ('ASO Savings and Loans', 'ASO Savings and Loans'), ('CEMCS Microfinance Bank', 'CEMCS Microfinance Bank'), ('Citibank Nigeria', 'Citibank Nigeria'), ('Ecobank Nigeria', 'Ecobank Nigeria'), ('Ekondo Microfinance Bank', 'Ekondo Microfinance Bank'), ('Fidelity Bank', 'Fidelity Bank'), ('First Bank of Nigeria', 'First Bank of Nigeria'), ('First City Monument Bank', 'First City Monument Bank'), ('Globus Bank', 'Globus Bank'), ('Guaranty Trust Bank', 'Guaranty Trust Bank'), ('Hasal Microfinance Bank', 'Hasal Microfinance Bank'), ('Heritage Bank', 'Heritage Bank'), ('Jaiz Bank', 'Jaiz Bank'), ('Keystone Bank', 'Keystone Bank'), ('Kuda Bank', 'Kuda Bank'), ('Parallex Bank', 'Parallex Bank'), ('Polaris Bank', 'Polaris Bank'), ('Providus Bank', 'Providus Bank'), ('Rubies MFB', 'Rubies MFB'), ('Sparkle Microfinance Bank', 'Sparkle Microfinance Bank'), ('Stanbic IBTC Bank', 'Stanbic IBTC Bank'), ('Standard Chartered Bank', 'Standard Chartered Bank'), ('Sterling Bank', 'Sterling Bank'), ('Suntrust Bank', 'Suntrust Bank'), ('TAJ Bank', 'TAJ Bank'), ('TCF MFB', 'TCF MFB'), ('Titan Bank', 'Titan Bank'), ('Union Bank of Nigeria', 'Union Bank of Nigeria'), ('United Bank For Africa', 'United Bank For Africa'), ('Unity Bank', 'Unity Bank'), ('VFD', 'VFD'), ('Wema Bank', 'Wema Bank'), ('Zenith Bank', 'Zenith Bank')]
categories = [('Agriculture', 'Agriculture'), ('Business', 'Business'), ('Education', 'Education'), ('Entertainment', 'Entertainment'), ('Events', 'Events'), ('Others', 'Others'), ('Parties', 'Parties'), ('Real Estate', 'Real Estate'), ('Seminars', 'Seminars'), ('Shopping', 'Shopping'), ('Sports', 'Sports'), ('Workshops', 'Workshops')]

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
	email = StringField('', validators=[Email('Please fill in a valid email address')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PasswordResetForm, self).__init__(*args, **kwargs)

class DepositForm(FlaskForm):
	amount = IntegerField('', validators=[DataRequired('Please fill in the amount you would like to deposit'), NumberRange(min=3000, message='minimum amount  is N3000')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(DepositForm, self).__init__(*args, **kwargs)

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

class PostForm(FlaskForm):
	title = StringField('Title <span class="text-muted">*</span>', validators=[DataRequired('Please fill in the title of your post'), Length(max=50)])
	link = StringField('Link <span class="text-muted">*</span>', validators=[URL('Please fill in a valid URL')])
	category = SelectField('Category <span class="text-muted">*</span>', choices=categories)
	description = TextAreaField('Short Description <span class="text-muted">*</span>', validators=[DataRequired('Please fill in a short description of your post'), Length(min=10, max=250)])
	image = FileField('', validators=[FileAllowed(['jpg','png', 'jpeg','JPG','JPEG','PNG'])])
	posters = IntegerField('Posters needed <span class="text-muted">*</span>', validators=[NumberRange(min=5, message='minimum amount of posters is 5')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PostForm, self).__init__(*args, **kwargs)

class PostSearchForm(FlaskForm):
	category = SelectField('Category', choices=categories)

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PostSearchForm, self).__init__(*args, **kwargs)

class FAQForm(FlaskForm):
	question = StringField('Question', validators=[DataRequired()])
	answer = TextAreaField('Answer', validators=[DataRequired()])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(FAQForm, self).__init__(*args, **kwargs)