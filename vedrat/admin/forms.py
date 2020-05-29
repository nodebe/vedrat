from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, ValidationError, Email

blogpostsubject = [('Withdrawal','Withdrawal'),('Deposit','Deposit'),('News','News')]
status = [('paid','Paid'),('pending','Pending')]
banks = [('Access Bank', 'Access Bank'), ('Access Bank (Diamond)', 'Access Bank (Diamond)'), ('ALAT by WEMA', 'ALAT by WEMA'), ('ASO Savings and Loans', 'ASO Savings and Loans'), ('CEMCS Microfinance Bank', 'CEMCS Microfinance Bank'), ('Citibank Nigeria', 'Citibank Nigeria'), ('Ecobank Nigeria', 'Ecobank Nigeria'), ('Ekondo Microfinance Bank', 'Ekondo Microfinance Bank'), ('Fidelity Bank', 'Fidelity Bank'), ('First Bank of Nigeria', 'First Bank of Nigeria'), ('First City Monument Bank', 'First City Monument Bank'), ('Globus Bank', 'Globus Bank'), ('Guaranty Trust Bank', 'Guaranty Trust Bank'), ('Hasal Microfinance Bank', 'Hasal Microfinance Bank'), ('Heritage Bank', 'Heritage Bank'), ('Jaiz Bank', 'Jaiz Bank'), ('Keystone Bank', 'Keystone Bank'), ('Kuda Bank', 'Kuda Bank'), ('Parallex Bank', 'Parallex Bank'), ('Polaris Bank', 'Polaris Bank'), ('Providus Bank', 'Providus Bank'), ('Rubies MFB', 'Rubies MFB'), ('Sparkle Microfinance Bank', 'Sparkle Microfinance Bank'), ('Stanbic IBTC Bank', 'Stanbic IBTC Bank'), ('Standard Chartered Bank', 'Standard Chartered Bank'), ('Sterling Bank', 'Sterling Bank'), ('Suntrust Bank', 'Suntrust Bank'), ('TAJ Bank', 'TAJ Bank'), ('TCF MFB', 'TCF MFB'), ('Titan Bank', 'Titan Bank'), ('Union Bank of Nigeria', 'Union Bank of Nigeria'), ('United Bank For Africa', 'United Bank For Africa'), ('Unity Bank', 'Unity Bank'), ('VFD', 'VFD'), ('Wema Bank', 'Wema Bank'), ('Zenith Bank', 'Zenith Bank')]


class FAQForm(FlaskForm):
	question = StringField('Question', validators=[DataRequired()])
	answer = TextAreaField('Answer', validators=[DataRequired()])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(FAQForm, self).__init__(*args, **kwargs)

class AddBlogPostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	subject = SelectField('Subject', choices=blogpostsubject, validators=[DataRequired()])
	image = FileField('Image', validators=[FileAllowed(['jpg','png', 'jpeg','JPG','JPEG','PNG'])])
	post = TextAreaField('Body', validators=[DataRequired()])
	poster = StringField('Poster', validators=[Length(max=30), DataRequired()])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(AddBlogPostForm, self).__init__(*args, **kwargs)

class WithdrawListSearchForm(FlaskForm):
	status = SelectField('Category', choices=status)

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(WithdrawListSearchForm, self).__init__(*args, **kwargs)

class UserEditForm(FlaskForm):
	fullname = StringField('Full name', validators=[DataRequired('Please fill in a username'), Length(min=3,max=30)])
	email = StringField('Email', validators=[DataRequired('Please fill in a valid email address')])
	phone = IntegerField('Phone')
	bank_name = SelectField('Bank name', choices=banks)
	acc_name = StringField('Account name')
	acc_number = IntegerField('Account number')
	plan = SelectField('Plan', choices=[('0','0'),('A','A'),('B','B')],validators=[DataRequired()])
	balance = IntegerField('Balance')
	account_status = SelectField('Account status', choices=(['open','open'],['blocked','blocked']))
	ad_earning = IntegerField('Ad earning')
	refer_earning = IntegerField('Refer earning')
	user_status = SelectField('User status', choices=[('member','member'),('admin','admin')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(UserEditForm, self).__init__(*args, **kwargs)

class BlockedUsersForm(FlaskForm):
	status = SelectField('Category', choices=[('blocked','blocked')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(BlockedUsersForm, self).__init__(*args, **kwargs)

class BlockedPostsForm(FlaskForm):
	status = SelectField('Category', choices=[('blocked','blocked'),('suspended','suspended')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(BlockedPostsForm, self).__init__(*args, **kwargs)