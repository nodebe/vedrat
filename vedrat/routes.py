import secrets
import os
import random
import json
import flask
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flask_mail import Mail, Message
from vedrat import app, db#, mail
from vedrat.utils import unique_id, save_picture
from vedrat.forms import UserRegForm, UserLogForm, PasswordResetForm, ContactForm, PasswordChangeForm, SettingsForm
from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, logout_user, login_required
from vedrat.models import User, Contact, Post, FAQ, PickedPost#, Transactiondb
from datetime import datetime as dt
'''from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from google_currency import convert

paystack_secret_key = 'sk_test_f9c2c409686a868572173088df9edc9cafa55598'
paystack = Paystack(secret_key = paystack_secret_key)
paystack.transaction.list()'''

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html', title='Home')

@app.route('/index/<string:referrer_id>')
def index_referrer(referrer_id):
	session['referrer_id'] = referrer_id
	return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('userdashboard'))
	if session['referrer_id']:
		referrer_id = session['referrer_id']
	else:
		referrer_id = ''
	form = UserRegForm()
	if form.validate_on_submit():
		hashed_password = sha256.encrypt(str(form.password.data))
		user = User(fullname=form.fullname.data,email=form.email.data,password=hashed_password, referrer=referrer_id)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created successfully.', 'success')
		return redirect(url_for('signin'))
	return render_template('signup.html', form=form, title='Register')

@app.route('/signin', methods=['GET','POST'])
def signin():
	if current_user.is_authenticated:
		return redirect(url_for('userdashboard'))
	form = UserLogForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and sha256.verify(form.password.data, user.password):
			login_user(user)
			next_page = request.args.get('next')
			if next_page and current_user.plan=='0' and 'userdashboard' not in next_page:
				flash('Please visit the payment page to pay for a plan and start earning', 'info')
			return redirect(next_page) if next_page else redirect(url_for('userdashboard'))
		else: 
			flash('Login Unsuccessful. Email or password invalid', 'danger')
	return render_template('signin.html', form=form, title='Login')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('signin'))

@app.route('/userdashboard')
@login_required
def userdashboard():
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	if current_user.plan=='0':
		flash('Please visit the payment page to pay for a plan and start earning', 'info')
	return render_template('userdashboard.html', title='Dashboard', shared=len(picked_ads), posted=len(shared_ads))

@app.route('/usersettings', methods=['GET','POST'])
@login_required
def usersettings():
	form = SettingsForm()
	passwordform = PasswordChangeForm()
	if form.validate_on_submit():
		current_user.fullname = form.fullname.data
		current_user.email = form.email.data
		current_user.phone = '0'+str(form.phone.data)
		current_user.bank_name = form.bank_name.data
		current_user.acc_number = form.acc_number.data
		current_user.acc_name = form.acc_name.data
		db.session.commit()
		flash('Your info has been updated', 'success')
		return redirect(url_for('usersettings'))
	elif request.method == 'GET':
		form.fullname.data = current_user.fullname
		form.email.data = current_user.email
		form.phone.data = current_user.phone
		form.bank_name.data = current_user.bank_name
		form.acc_number.data = current_user.acc_number
		form.acc_name.data = current_user.acc_name

	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('settings.html', title='Settings', shared=len(picked_ads), posted=len(shared_ads), form=form, pform=passwordform)

@app.route('/changepassword', methods=['POST'])
def changepassword():
	pform = PasswordChangeForm()
	if pform.validate_on_submit():
		if sha256.verify(pform.oldpassword.data, current_user.password):
			current_user.password = sha256.encrypt(str(pform.newpassword.data))
			db.session.commit()
			flash('Password changed successfully', 'success')
			return redirect(url_for('usersettings'))
		else:
			flash('Your password does not match', 'info')
			return redirect(url_for('usersettings'))
	else:
		flash('Your password does not match', 'info')
		return redirect(url_for('usersettings'))

'''
@app.route('/passwordreset', methods=['GET','POST'])
def passwordreset():
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			new_password = unique_id()
			hashed_password = sha256.encrypt(str(new_password))
			user.password = hashed_password
			db.session.commit()
			#send email with new_password
			msg = Message('Password Reset for vedrat Goldmines', sender='noreply@vedratgoldmines.com', recipients=[user.email])
			msg.body = "%s"%(new_password)
			mail.send(msg)
			flash('Password reset Successful, Check your Email for your new password', 'success')
			return redirect(url_for('signin'))
		else:
			flash('Password reset Unsuccessful, Invalid Email', 'danger')
	return render_template('passwordreset.html', form=form)
'''

@app.route('/contact', methods=['GET','POST'])
def contact():
	form = ContactForm()
	if current_user.is_authenticated:
		if request.method == 'GET':
			form.fullname.data = current_user.fullname
			form.email.data = current_user.email
	if form.validate_on_submit():
		contact = Contact(fullname=form.fullname.data,email=form.email.data,subject=form.subject.data,message=form.message.data)
		db.session.add(contact)
		db.session.commit()
		flash('Your message has been posted successfully. We will get back to you through an email message', 'success')
		return redirect(url_for('contact'))
	return render_template('contact.html', title='Contact', form=form)

'''
@app.route('/vmessage', methods=['GET','POST'])
@login_required
def vmessages():
	if current_user.user_status == 'admin':
		messages = Contact.query.all()
		return render_template('vmessages.html', messages=messages)
	else:
		return redirect(url_for('signin'))

@app.route('/vmess/<string:uuid>', methods=['GET','POST'])
@login_required
def vmess(uuid):
	if current_user.user_status == 'admin':
		message = Contact.query.filter_by(uuid=uuid).first()
		message.read = 1
		db.session.commit()
		return render_template('vmess.html', message=message)
	else:
		return redirect(url_for('signin'))

@app.route('/delete/<string:uuid>', methods=['GET','POST'])
@login_required
def delete(uuid):
	if current_user.user_status == 'admin':
		message = Contact.query.filter_by(uuid=uuid).first()
		# delete_me(r"static/img", ebook.thumbnail)
		db.session.delete(message)
		db.session.commit()
		flash('The message has been deleted successfully', 'success')
		return redirect(url_for('vmessages'))
	else:
		return redirect(url_for('signin'))
'''
