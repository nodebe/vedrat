from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from flask_mail import Mail, Message
from vedrat import app, db, mail
from datetime import datetime as dt
from vedrat.utils import unique_id, date_stuff, referral_earning, date_compare
from vedrat.users.forms import UserRegForm, UserLogForm, PasswordResetForm, PasswordChangeForm, SettingsForm
from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, logout_user, login_required
from vedrat.models import User, Contact, Post, FAQ, PickedPost

users = Blueprint('users', __name__)

error_message = 'Error on our side, try again later!'

@users.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('users.userdashboard'))
	if "referrer_id" in session:
		referrer_id = session['referrer_id']
	else:
		referrer_id = ''
	form = UserRegForm()
	if form.validate_on_submit():
		uuid = unique_id()
		hashed_password = sha256.encrypt(str(form.password.data))
		try:
			user = User(fullname=form.fullname.data,email=form.email.data,password=hashed_password, referrer=referrer_id, uuid=uuid)
			db.session.add(user)
			db.session.commit()
			flash('Your account has been created successfully.', 'success')
			return redirect(url_for('users.signin'))
		except Exception as e:
			flash(error_message, 'warning')
			return redirect(url_for('users.signup'))	
	return render_template('signup.html', form=form, title='Register')

@users.route('/signin', methods=['GET','POST'])
def signin():
	if current_user.is_authenticated:
		return redirect(url_for('users.userdashboard'))
	form = UserLogForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and sha256.verify(form.password.data, user.password):
			if user.account_status != 'blocked':
				login_user(user)
				next_page = request.args.get('next')
				if next_page and current_user.plan=='0' and 'userdashboard' not in next_page:
					flash('Please visit the payment page to pay for a plan and start earning', 'info')
				return redirect(next_page) if next_page else redirect(url_for('users.userdashboard'))
			else:
				flash('Login Unsuccessful. Account Blocked!', 'warning')
		else: 
			flash('Login Unsuccessful. Email or password invalid', 'danger')
	return render_template('signin.html', form=form, title='Login')

@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('users.signin'))

@users.route('/userdashboard')
@login_required
def userdashboard():
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(post_status='open').order_by(Post.id.desc()).paginate(page=page,per_page=8)

	refer_balance = referral_earning()
	withdraw_date = date_compare()

	if dt.now().strftime('%Y-%m-%d') > withdraw_date:
		current_user.plan = '0'

	if current_user.ad_collected_date != date_stuff():
		current_user.ad_collected_on_day = 0
		current_user.can_post = 1
		db.session.commit()

	if current_user.plan=='0':
		flash('Please visit the payment page to pay for a plan and start earning', 'info')
	return render_template('userdashboard.html', title='Dashboard', shared=len(picked_ads), posted=len(shared_ads), posts=posts, refer_balance=refer_balance)

@users.route('/usersettings', methods=['GET','POST'])
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
		return redirect(url_for('users.usersettings'))
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

@users.route('/changepassword', methods=['POST'])
@login_required
def changepassword():
	pform = PasswordChangeForm()
	if pform.validate_on_submit():
		try:
			if sha256.verify(pform.oldpassword.data, current_user.password):
				current_user.password = sha256.encrypt(str(pform.newpassword.data))
				db.session.commit()
				flash('Password changed successfully', 'success')
			else:
				flash('Your password does not match', 'info')
		except Exception as e:
			flash(error_message, 'warning')
		finally:
			return redirect(url_for('users.usersettings'))
	else:	
		flash('Your password does not match', 'info')
		return redirect(url_for('users.usersettings'))

@users.route('/userposts')
@login_required
def userposts():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(poster_id=current_user.uuid).order_by(Post.id.desc()).paginate(page=page,per_page=8)
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('userposts.html', title='My ads', posts=posts, shared=len(picked_ads), posted=len(shared_ads))

@users.route('/userapplypost/<string:post_id>')
@login_required
def userapplypost(post_id):
	try:
		if current_user.can_post == 1:
			post = Post.query.filter_by(uuid=post_id).first()

			date = date_stuff()

			current_user.ad_collected_date = date
			current_user.ad_collected_on_day += 1
			post.posters_applied += 1

			#deciding if a user can post or not based on his plan
			if current_user.plan=='B' and current_user.ad_collected_on_day == 2:
				current_user.can_post = 0
			elif current_user.plan=='A' and current_user.ad_collected_on_day == 1:
				current_user.can_post = 0

			short_link_id = str(unique_id())
			short_linker = 'https://www.vedrat.com/ad_post/'+ short_link_id

			picked = PickedPost(post_id=post_id,picker_id=current_user.uuid,main_link=post.link,web_link=short_linker, description=post.description, uuid=short_link_id)

			db.session.add(picked)
			db.session.commit()

			picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
			shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
			return render_template('userapplypost.html', title=post.title, shared=len(picked_ads), posted=len(shared_ads), post=post,picked=picked)
		else:
			return redirect(url_for('posts.sharedads'))
	except Exception as e:
		flash(error_message, 'warning')
		return redirect(url_for('posts.sharedads'))

@users.route('/viewsharedad/<string:uuid>')
@login_required
def viewsharedad(uuid):
	picked_post = PickedPost.query.filter_by(uuid=uuid).first()
	post = Post.query.filter_by(uuid=picked_post.post_id).first()

	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('viewsharedad.html', title=post.title, shared=len(picked_ads), posted=len(shared_ads), post=post, picked=picked_post)

@users.route('/passwordreset', methods=['GET','POST'])
def passwordreset():
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			try:
				new_password = unique_id()
				hashed_password = sha256.encrypt(str(new_password))
				user.password = hashed_password
				#send email with new_password
				msg = Message(subject='Password Reset | vedrat', recipients=[user.email])
				msg.html = "Your new password is <b>%s</b>"%(new_password)
				mail.send(msg)
				db.session.commit()
				flash('Password reset Successful, Check your Email for your new password', 'success')
				return redirect(url_for('users.signin'))
			except Exception as e:
				flash(error_message, 'warning')
		else:
			flash('Password reset Unsuccessful, Invalid Email', 'danger')
	return render_template('passwordreset.html', form=form, title='Reset password')
