import secrets
import os
import random
import json
import flask
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, session
from flask_mail import Mail, Message
from vedrat import app, db, mail
from vedrat.utils import unique_id, save_picture, date_stuff, referral_earning, date_compare, delete_picture
from vedrat.forms import UserRegForm, UserLogForm, PasswordResetForm, ContactForm, PasswordChangeForm, SettingsForm, PostForm, PostSearchForm, FAQForm, DepositForm
from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, logout_user, login_required
from vedrat.models import User, Contact, Post, FAQ, PickedPost, Withdrawals
from datetime import datetime as dt
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction

paystack_secret_key = 'sk_test_37408e2ede43f221bed5b6ab0d7ed78913f2b6dc'
paystack = Paystack(secret_key = paystack_secret_key)
#paystack.transaction.list()

@app.route('/')
@app.route('/index')
def index():
	popular_posts = Post.query.order_by(Post.posters_applied.desc()).limit(4).all()
	new_posts = Post.query.order_by(Post.id.desc()).limit(4).all()

	return render_template('index.html', title='Home', popular_posts=popular_posts, new_posts=new_posts)

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
		uuid = unique_id()
		hashed_password = sha256.encrypt(str(form.password.data))
		user = User(fullname=form.fullname.data,email=form.email.data,password=hashed_password, referrer=referrer_id, uuid=uuid)
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
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(post_status='open').order_by(Post.id.desc()).paginate(page=page,per_page=8)

	refer_balance = referral_earning()

	if current_user.ad_collected_date != date_stuff():
		current_user.ad_collected_on_day = 0
		current_user.can_post = 1
		db.session.commit()

	if current_user.plan=='0':
		flash('Please visit the payment page to pay for a plan and start earning', 'info')
	return render_template('userdashboard.html', title='Dashboard', shared=len(picked_ads), posted=len(shared_ads), posts=posts, refer_balance=refer_balance)

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
@login_required
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

@app.route('/reportpost/<string:post_id>')
@login_required
def reportpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	post.report += 1
	if post.report >= 5:
		post.post_status = 'blocked'
	db.session.commit()
	flash('You have reported the post', 'success')
	return redirect(url_for('userdashboard'))

@app.route('/postad', methods=["GET","POST"])
@app.route('/postad/<string:post_id>', methods=["GET","POST"])
@login_required
def postad(post_id=''):
	form = PostForm()
	if form.validate_on_submit():
		price = (300 * form.posters.data) - 10 * (form.posters.data - 1)
		if post_id=='':
			if (current_user.balance >= price):
				if form.image.data:
					image_name = save_picture(form.image.data)
				else:
					image_name = 'default_ad_image.png'
				post = Post(poster_id=current_user.uuid,title=form.title.data,link=form.link.data,description=form.description.data,posters_needed=form.posters.data,category=form.category.data,image=image_name)
				current_user.balance-=price
				db.session.add(post)
				db.session.commit()
				flash("Your ad has been successfully posted", 'success')
				return redirect(url_for('postad'))
			else:
				flash("You don't have enough balance to complete this action.", 'info')
				return render_template('postad.html', title='Post Ad', form=form)
		elif post_id != '':
			post = Post.query.filter_by(uuid=post_id).first()
			new_price = (300 * form.posters.data) - 10 * (form.posters.data - 1)
			initial_price = (300 * post.posters_needed) - 10 * (post.posters_needed - 1)
			if (form.posters.data > post.posters_needed):
				official_price = new_price - initial_price
				price_tag = 'remove'
			elif(form.posters.data < post.posters_needed):
				official_price = initial_price - new_price
				price_tag = 'add'
			else:
				official_price = 0
				price_tag = 'same'

			if (current_user.balance >= official_price):
				post.title = form.title.data
				post.link = form.link.data
				post.category = form.category.data
				post.description = form.description.data
				post.posters_needed = form.posters.data
				if post.image != 'default_ad_image.png':
					delete_picture(post.image)
				if form.image.data:
					post.image = save_picture(form.image.data)
				else:
					post.image = 'default_ad_image.png'
				if price_tag == 'remove':
					current_user.balance-=official_price
				elif price_tag == 'add':
					current_user.balance+=official_price
				db.session.commit()
				flash('Your post has been updated successfully', 'success')
				return redirect(url_for('userposts'))
			else:
				flash("You don't have enough balance to complete this action.", 'info')
				return render_template('postad.html/post.uuid', title='Post Ad', form=form)
		
	elif request.method == "GET" and post_id!='':
		post = Post.query.filter_by(uuid=post_id).first()
		if post.poster_id == current_user.uuid:
			form.title.data = post.title
			form.link.data = post.link
			form.category.data = post.category
			form.description.data = post.description
			form.posters.data = post.posters_needed
		else:
			return redirect(url_for('userdashboard'))
	
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('postad.html', title='Post Ad', form=form, shared=len(picked_ads), posted=len(shared_ads))

@app.route('/userposts')
@login_required
def userposts():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(poster_id=current_user.uuid).order_by(Post.id.desc()).paginate(page=page,per_page=8)
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('userposts.html', title='My ads', posts=posts, shared=len(picked_ads), posted=len(shared_ads))

@app.route('/usersuspendpost/<string:post_id>')
@login_required
def usersuspendpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	if post.post_status == 'open':
		post.post_status = 'suspended'	
		flash("Post suspended and won't be seen by users", 'info')
	elif post.post_status == 'suspended':
		post.post_status = 'open'
		flash("Post opened and can be seen by users", 'info')
	db.session.commit()
	return redirect(url_for('userposts'))

@app.route('/userviewpost/<string:post_id>')
@login_required
def userviewpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	return render_template('userviewpost.html', title=post.title, post=post)

@app.route('/userdeletepost/<string:post_id>')
@login_required
def userdeletepost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	if post.poster_id == current_user.uuid or current_user.user_status == 'admin':
		initial_price = (300 * post.posters_needed) - 10 * (post.posters_needed - 1)
		current_price = (300 * post.posters_applied) - 10 * (post.posters_applied - 1)
		user_balance = initial_price - current_price
		current_user.balance+=user_balance
		db.session.delete(post)
		db.session.commit()
		flash('Post deleted successfully.','info')
		return redirect(url_for('userposts'))
	else:
		return redirect(url_for('userdashboard'))

@app.route('/newposts', methods=['GET','POST'])
@login_required
def newposts():
	form = PostSearchForm()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.filter_by(post_status='open').order_by(Post.id.desc()).paginate(page=page,per_page=8)

	if form.validate_on_submit():
		posts = Post.query.filter_by(post_status='open').filter_by(category=form.category.data).order_by(Post.id.desc()).paginate(page=page,per_page=8)

	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('newposts.html', title='New posts', form=form, shared=len(picked_ads), posted=len(shared_ads), posts=posts)

@app.route('/sharedads')
@login_required
def sharedads():
	page = request.args.get('page', 1, type=int)
	picked_posts = PickedPost.query.filter_by(picker_id=current_user.uuid).order_by(PickedPost.id.desc()).paginate(page=page,per_page=8)
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('sharedads.html', title='Shared ads', shared=len(picked_posts.items), posted=len(shared_ads), posts=picked_posts)

@app.route('/userapplypost/<string:post_id>')
@login_required
def userapplypost(post_id):
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
		short_linker = 'http://127.0.0.1:5000/ad_post/'+ short_link_id

		picked = PickedPost(post_id=post_id,picker_id=current_user.uuid,main_link=post.link,web_link=short_linker, description=post.description, uuid=short_link_id)

		db.session.add(picked)
		db.session.commit()

		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('userapplypost.html', title=post.title, shared=len(picked_ads), posted=len(shared_ads), post=post,picked=picked)
	else:
		return redirect(url_for('sharedads'))


@app.route('/viewsharedad/<string:uuid>')
@login_required
def viewsharedad(uuid):
	picked_post = PickedPost.query.filter_by(uuid=uuid).first()
	post = Post.query.filter_by(uuid=picked_post.post_id).first()

	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('viewsharedad.html', title=post.title, shared=len(picked_ads), posted=len(shared_ads), post=post, picked=picked_post)

@app.route('/faq')
def faq():
	faqs = FAQ.query.all()

	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('faq.html', title='Frequently Asked Questions', shared=len(picked_ads), posted=len(shared_ads), faqs=faqs)

@app.route('/postfaq', methods=['GET','POST'])
@login_required
def postfaq():
	if current_user.user_status == 'admin':
		form = FAQForm()
		if form.validate_on_submit():
			addfaq = FAQ(question=form.question.data,answer=form.answer.data)
			db.session.add(addfaq)
			db.session.commit()
			flash('Faq added successfully', 'success')
			return redirect(url_for('postfaq'))

		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('postfaq.html', title='Post FAQ', shared=len(picked_ads), posted=len(shared_ads), form=form)
	else:
		return redirect(url_for('userdashboard'))


@app.route('/passwordreset', methods=['GET','POST'])
def passwordreset():
	form = PasswordResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			new_password = unique_id()
			hashed_password = sha256.encrypt(str(new_password))
			user.password = hashed_password
			#send email with new_password
			msg = Message(subject='Password Reset | vedrat', recipients=[user.email])
			msg.html = "Your new password is <b>%s</b>"%(new_password)
			mail.send(msg)
			db.session.commit()
			flash('Password reset Successful, Check your Email for your new password', 'success')
			return redirect(url_for('signin'))
		else:
			flash('Password reset Unsuccessful, Invalid Email', 'danger')
	return render_template('passwordreset.html', form=form)


@app.route('/ad_post/<string:url>')
def ad_post(url):
    link_ad = PickedPost.query.filter_by(uuid=url).first()
    picker = User.query.filter_by(uuid=link_ad.picker_id).first()
    if link_ad.clicks == 0:
    	picker.ad_earning+=280
    link_ad.clicks+=1
    db.session.commit()
    return redirect(link_ad.main_link)

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

@app.route('/userpayment')
def userpayment():
	if current_user.is_authenticated:
		form = DepositForm()
		refer_balance = referral_earning()
		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('userpayment.html', title='Payment', shared=len(picked_ads), posted=len(shared_ads),refer_balance=refer_balance, form=form)
	else:
		return render_template('userpayment.html', title='Payment', shared=0, posted=0)

@app.route('/pay_plan_<string:plan_id>')
@login_required
def pay_plan(plan_id):
	if current_user.plan == '0':
		transaction_id = plan_id.upper()+'_'+current_user.uuid+'_'+unique_id()
		current_user.verify_id_code = transaction_id
		db.session.commit() 
		if plan_id == 'a':
			response = Transaction.initialize(reference=transaction_id,amount=300000, email=current_user.email)
			return redirect(response['data']['authorization_url'])
		elif plan_id == 'b':
			response = Transaction.initialize(reference=transaction_id,amount=500000, email=current_user.email)
			return redirect(response['data']['authorization_url'])
	else:
		flash('You are already subscribed to a plan ' + str(current_user.plan), 'warning')
	return redirect('userpayment')

@app.route('/verify_transaction')
@login_required
def verify_transaction():
	verify = Transaction.verify(reference=current_user.verify_id_code)
	referred_by = current_user.referrer
	if referred_by != '':
		referrer = User.query.filter_by(uuid=referred_by).first()
	if verify['data']['status'] == 'success':
		if current_user.verify_id_code.startswith('WB'):
			current_user.balance += verify['data']['requested_amount']/100
		else:
			current_user.date_of_payment = dt.strptime(verify['data']['transaction_date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
			if verify['data']['requested_amount'] == 300000:
				current_user.plan = 'A'
				if referred_by != '':
					referrer.refer_earning += 300
					referrer.referred_plan_1 += 1
					current_user.referrer = ''
			elif verify['data']['requested_amount'] == 500000:
				current_user.plan = 'B'
				if referred_by != '':
					referrer.refer_earning += 500
					referrer.referred_plan_2 += 1
					current_user.referrer = ''
		db.session.commit()
		flash('You have successfully subscribed!', 'success')
		return redirect(url_for('userdashboard'))
	else:
		flash('Your subscription was not successful!', 'info')
		return redirect(url_for('userpayment'))

@app.route('/wb_deposit', methods=['POST'])
@login_required
def wb_deposit():
	form = DepositForm()
	if form.validate_on_submit():
		transaction_id = 'WB'+'_'+current_user.uuid+'_'+unique_id()
		current_user.verify_id_code = transaction_id
		db.session.commit()
		response = Transaction.initialize(reference=transaction_id,amount=form.amount.data*100, email=current_user.email)
		return redirect(response['data']['authorization_url'])
	else:
		flash('Deposit not approved', 'warning')
		return redirect(url_for('userpayment'))

@app.route('/withdraw_balance')
@login_required
def withdraw_balance():
	if current_user.date_of_payment != None:
		withdraw_date = date_compare()
		new_date = dt.now().strftime('%Y-%m-%d')
		if current_user.bank_name!='' and current_user.acc_name!='' and current_user.acc_number!='':
			if new_date >= withdraw_date:
				try:
					withdraw_amount = current_user.ad_earning + referral_earning()
					withdraw = Withdrawals(uuid_of_user=current_user.uuid,bank_name=current_user.bank_name,acc_number=current_user.acc_number,acc_name=current_user.acc_name, amount=withdraw_amount, status='pending')
					current_user.referred_plan_1 = 0
					current_user.referred_plan_2 = 0
					current_user.ad_earning = 0
					current_user.refer_earning = 0
					current_user.plan = '0'
					current_user.date_of_payment = None
					db.session.add(withdraw)
					db.session.commit()
					flash('You will be credited within the next 24 hours', 'success')
					return redirect(url_for('userpayment'))
				except Exception as e:
					flash('Error on our side. please try again later' + str(e), 'warning')
					return redirect(url_for('userpayment'))
			else:
				d1 = dt.strptime(withdraw_date, '%Y-%m-%d')
				d2 = dt.strptime(new_date, '%Y-%m-%d')
				flash('You have {} more days till you can make a withdrawal '.format(abs((d1-d2).days)), 'info')
				return redirect(url_for('userpayment'))
		else:
			flash('Please update your bank information', 'info')
			return redirect(url_for('usersettings'))
	else:
		flash('You have to be subscribed to a plan', 'info')
		return redirect(url_for('userpayment'))

@app.route('/withdrawals_list')
@login_required
def withdrawals_list():
	if current_user.user_status == 'admin':
		page = request.args.get('page', 1, type=int)
		withdrawals = Withdrawals.query.order_by(Withdrawals.id.desc()).paginate(page=page,per_page=10)
		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('withdrawals_list.html', title='Withdrawals', shared=len(picked_ads), posted=len(shared_ads),withdrawals=withdrawals)
	else:
		return redirect(url_for('userdashboard'))

@app.route('/verify_withdraw/<string:uuid>')
@login_required
def verify_withdraw(uuid):
	if current_user.user_status == 'admin':
		withdraw = Withdrawals.query.filter_by(uuid=uuid).first()
		withdraw.status = 'paid'
		db.session.commit()
		flash('Updated successfully', 'success')
		return redirect(url_for('withdrawals_list'))
	else:
		return redirect(url_for('userdashboard'))

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
		'''