import secrets
import random
import os
from vedrat import app
from PIL import Image
from resizeimage import resizeimage
from datetime import datetime as dt
from datetime import timedelta
from flask_login import current_user

def unique_id():
    token = secrets.token_hex(16)[:7]
    new_token = ' '.join(token).split(' ')
    main_id = ''.join(random.sample(new_token, len(new_token)-1))
    return (main_id)

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img/vedrat', picture_fn)
	picture_path_100 = os.path.join(app.root_path, 'static/img/vedrat/100', picture_fn)
	
	i = Image.open(form_picture)
	i = resizeimage.resize_cover(i, [520, 400], validate=False)
	j = resizeimage.resize_cover(i, [100, 100], validate=False)
	i.save(picture_path)
	j.save(picture_path_100)
	
	return picture_fn

def save_blog_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/img/vedrat/blog', picture_fn)
	picture_path_950 = os.path.join(app.root_path, 'static/img/vedrat/blog/950', picture_fn)
	
	i = Image.open(form_picture)
	i = resizeimage.resize_cover(i, [520, 400], validate=False)
	j = resizeimage.resize_cover(i, [950, 500], validate=False)
	i.save(picture_path)
	j.save(picture_path_950)
	
	return picture_fn

def delete_picture(pic_name):
	picture_path = os.path.join(app.root_path, 'static/img/vedrat', pic_name)
	picture_path_100 = os.path.join(app.root_path, 'static/img/vedrat/100', pic_name)
	os.remove(picture_path_100)
	os.remove(picture_path)

#returns the current date
def date_stuff():
	date = dt.now()
	post_date = date.strftime('%Y-%m-%d')
	return (str(post_date))

def date_compare():
	date = current_user.date_of_payment
	if date != None:
		if current_user.plan != 'C':
			adjusted = date + timedelta(days=25)
		elif current_user.plan == 'C':
			adjusted = date + timedelta(days=13)
			date = adjusted.strftime('%Y-%m-%d')
	else:
		date = dt.now().strftime('%Y-%m-%d')
	return date

def referral_earning():
	referred_1 = current_user.referred_plan_1
	referred_2 = current_user.referred_plan_2
	if referred_1 >= 10:
		refer_balance_1 = (referred_1 * 300) + 3000
	elif referred_1 >= 20:
		refer_balance_1 = (referred_1 * 300) + 7000
	elif referred_1 >= 50:
		refer_balance_1 = (referred_1 * 300) + 20000
	else:
		refer_balance_1 = referred_1 * 300

	if referred_2 >= 10:
		refer_balance_2 = (referred_2 * 500) + 5000
	elif referred_2 >= 20:
		refer_balance_2 = (referred_2 * 500) + 12000
	elif referred_2 >= 50:
		refer_balance_2 = (referred_2 * 500) + 36000
	else:
		refer_balance_2 = referred_2 * 500

	refer_balance = refer_balance_1+refer_balance_2

	return refer_balance

user_pay = 280
user_pay_c = 96
advertiser_pay = 168
refer_pay = 0.1

from vedrat.models import User
