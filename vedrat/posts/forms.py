from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, IntegerField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, URL, NumberRange

categories = [('Agriculture', 'Agriculture'), ('Business', 'Business'), ('Education', 'Education'), ('Entertainment', 'Entertainment'), ('Events', 'Events'), ('Others', 'Others'), ('Parties', 'Parties'), ('Real Estate', 'Real Estate'), ('Seminars', 'Seminars'), ('Shopping', 'Shopping'), ('Sports', 'Sports'), ('Workshops', 'Workshops')]

class PostForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired('Please fill in the title of your post'), Length(max=50)])
	link = StringField('Link', validators=[URL('Please fill in a valid URL')])
	category = SelectField('Category', choices=categories)
	description = TextAreaField('Short Description', validators=[DataRequired('Please fill in a short description of your post'), Length(min=10, max=250)])
	image = FileField('', validators=[FileAllowed(['jpg','png', 'jpeg','JPG','JPEG','PNG'])])
	posters = IntegerField('Posters needed', validators=[NumberRange(min=5, message='minimum amount of posters is 5')])
	
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PostForm, self).__init__(*args, **kwargs)

class PostSearchForm(FlaskForm):
	category = SelectField('Category', choices=categories)

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(PostSearchForm, self).__init__(*args, **kwargs)
