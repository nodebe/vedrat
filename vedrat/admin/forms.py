from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length

blogpostsubject = (['Withdrawal','Withdrawal'],['Deposit','Deposit'],['News','News'])

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