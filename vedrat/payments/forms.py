from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

class DepositForm(FlaskForm):
	amount = IntegerField('', validators=[DataRequired('Please fill in the amount you would like to deposit'), NumberRange(min=3000, message='minimum amount  is N3000')])

	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		super(DepositForm, self).__init__(*args, **kwargs)