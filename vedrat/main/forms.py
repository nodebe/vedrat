from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email

class ContactForm(FlaskForm):
	fullname = StringField('Fullname <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your name'),Length(min=4,max=20)])
	message = TextAreaField('Message <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your message')])
	subject = SelectField('Subject <span class="text-muted">*</span>',choices=[('Making a deposit','Making a deposit'),('Making a withdrawal','Making a withdrawal'),('Posting an ad','Posting an ad'),('Login issues','Login issues'),('Signup issues','Signup issues'),('Others..','Others..') ], validators=[DataRequired('Please fill the subject of the message')])
	email = StringField('Email <span class="text-muted">*</span>', validators=[Email('Please fill in a valid email address')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(ContactForm, self).__init__(*args, **kwargs)

class BlogreplyForm(FlaskForm):
	fullname = StringField('Fullname <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your name'),Length(min=4,max=20)])
	message = TextAreaField('Message <span class="text-muted">*</span>', validators=[DataRequired('Please fill in your message')])
	email = StringField('Email <span class="text-muted">*</span>', validators=[Email('Please fill in a valid email address')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(BlogreplyForm, self).__init__(*args, **kwargs)