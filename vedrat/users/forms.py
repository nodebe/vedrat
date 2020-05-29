from vedrat.models import User
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

banks = [('Access Bank', 'Access Bank'), ('Access Bank (Diamond)', 'Access Bank (Diamond)'), ('ALAT by WEMA', 'ALAT by WEMA'), ('ASO Savings and Loans', 'ASO Savings and Loans'), ('CEMCS Microfinance Bank', 'CEMCS Microfinance Bank'), ('Citibank Nigeria', 'Citibank Nigeria'), ('Ecobank Nigeria', 'Ecobank Nigeria'), ('Ekondo Microfinance Bank', 'Ekondo Microfinance Bank'), ('Fidelity Bank', 'Fidelity Bank'), ('First Bank of Nigeria', 'First Bank of Nigeria'), ('First City Monument Bank', 'First City Monument Bank'), ('Globus Bank', 'Globus Bank'), ('Guaranty Trust Bank', 'Guaranty Trust Bank'), ('Hasal Microfinance Bank', 'Hasal Microfinance Bank'), ('Heritage Bank', 'Heritage Bank'), ('Jaiz Bank', 'Jaiz Bank'), ('Keystone Bank', 'Keystone Bank'), ('Kuda Bank', 'Kuda Bank'), ('Parallex Bank', 'Parallex Bank'), ('Polaris Bank', 'Polaris Bank'), ('Providus Bank', 'Providus Bank'), ('Rubies MFB', 'Rubies MFB'), ('Sparkle Microfinance Bank', 'Sparkle Microfinance Bank'), ('Stanbic IBTC Bank', 'Stanbic IBTC Bank'), ('Standard Chartered Bank', 'Standard Chartered Bank'), ('Sterling Bank', 'Sterling Bank'), ('Suntrust Bank', 'Suntrust Bank'), ('TAJ Bank', 'TAJ Bank'), ('TCF MFB', 'TCF MFB'), ('Titan Bank', 'Titan Bank'), ('Union Bank of Nigeria', 'Union Bank of Nigeria'), ('United Bank For Africa', 'United Bank For Africa'), ('Unity Bank', 'Unity Bank'), ('VFD', 'VFD'), ('Wema Bank', 'Wema Bank'), ('Zenith Bank', 'Zenith Bank')]

class UserRegForm(FlaskForm):
	fullname = StringField('', validators=[DataRequired('Please fill in a username'), Length(min=3,max=30)])
	email = StringField('', validators=[DataRequired('Please fill in a valid email address')])
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
		validators=[DataRequired('Please fill in a valid email address')])
	password = PasswordField('',
		validators=[DataRequired('Please fill in your password')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(UserLogForm, self).__init__(*args, **kwargs)

class PasswordResetForm(FlaskForm):
	email = StringField('', validators=[DataRequired('Please fill in a valid email address')])

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
	email = StringField('', validators=[DataRequired('Please fill in a valid email address')])
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
