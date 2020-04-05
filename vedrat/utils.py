import secrets
import random
import os
from vedrat import app
from PIL import Image
from datetime import datetime as dt
from datetime import timedelta
#from paystackapi.transaction import Transaction

def unique_id():
    token = secrets.token_hex(16)[:7]
    new_token = ' '.join(token).split(' ')
    main_id = ''.join(random.sample(new_token, len(new_token)-1))
    return (main_id)

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
	
	output_size = (479, 340)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)
	
	return picture_fn
'''
def verify_user(reference):
	verify = Transaction.verify(reference=reference)
	if verify['data']['status'] == 'success':
		return 'success'
'''
from vedrat.models import User
