import secrets
import os
import random
import json
import flask
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_mail import Mail, Message
from vedrat import app, db#, mail
from vedrat.utils import unique_id, save_picture
from vedrat.forms import UserRegForm, UserLogForm, PasswordResetForm, ContactForm, PasswordChangeForm
from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, logout_user, login_required
from vedrat.models import User, Contact, Post, FAQ#, Transactiondb
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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('userdashboard'))
	form = UserRegForm()
	if form.validate_on_submit():
		hashed_password = sha256.encrypt(str(form.password.data))
		user = User(fullname=form.fullname.data,email=form.email.data,password=hashed_password)
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
			if current_user.plan=='0':
				flash('Please visit your payment page to pay for a plan and start earning', 'info')
			return redirect(next_page) if next_page else redirect(url_for('userdashboard'))
		else: 
			flash('Login Unsuccessful. Email or password invalid', 'danger')
	return render_template('signin.html', form=form, title='Login')

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('signin'))

@app.route('/userdashboard')
def userdashboard():
	if current_user.plan=='0':
		return 'Please visit your payment page to pay for a plan and start earning'
	return '<h1>Welcome, {}'.format(current_user.fullname)
	#return redirect(url_for('signin'))

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
	if form.validate_on_submit():
		contact = Contact(name=form.name.data,email=form.email.data,subject=form.subject.data,message=form.message.data,read='0')
		db.session.add(contact)
		db.session.commit()
		flash('Your message has been posted successfully. We will get back to you through an email message', 'success')
		return redirect(url_for('contact'))
	return render_template('contactform.html', title='Contact', form=form)

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
