from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class FAQForm(FlaskForm):
	question = StringField('Question', validators=[DataRequired()])
	answer = TextAreaField('Answer', validators=[DataRequired()])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(FAQForm, self).__init__(*args, **kwargs)