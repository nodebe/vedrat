from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from vedrat import app, db
from vedrat.utils import unique_id, save_blog_picture
from vedrat.admin.forms import FAQForm, AddBlogPostForm, WithdrawListSearchForm, UserEditForm, BlockedUsersForm
#from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, login_required
from vedrat.models import FAQ, Withdrawals, PickedPost, Post, Blogpost, Contact, User

admin = Blueprint('admin', __name__)

error_message = 'Error on our side, try again later!'

@admin.route('/postfaq', methods=['GET','POST'])
@login_required
def postfaq():
	if current_user.user_status == 'admin':
		try:
			form = FAQForm()
			if form.validate_on_submit():
				addfaq = FAQ(question=form.question.data,answer=form.answer.data)
				db.session.add(addfaq)
				db.session.commit()
				flash('Faq added successfully', 'success')
				return redirect(url_for('admin.postfaq'))

			picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
			shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
			return render_template('postfaq.html', title='Post FAQ', shared=len(picked_ads), posted=len(shared_ads), form=form)
		except Exception as e:
			flash(error_message, 'warning')
			return redirect(url_for('admin.postfaq'))
	else:
		abort(404)

@admin.route('/withdrawals_list', methods=['GET','POST'])
@login_required
def withdrawals_list():
	if current_user.user_status == 'admin':
		form = WithdrawListSearchForm()
		page = request.args.get('page', 1, type=int)
		withdrawals = Withdrawals.query.order_by(Withdrawals.id.desc()).paginate(page=page,per_page=10)
		if form.validate_on_submit():
			withdrawals = Withdrawals.query.filter_by(status=form.status.data).order_by(Withdrawals.id.desc()).paginate(page=page,per_page=10)
		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('withdrawals_list.html', title='Withdrawals', shared=len(picked_ads), posted=len(shared_ads),withdrawals=withdrawals,form=form)
	else:
		abort(404)

@admin.route('/verify_withdraw/<string:uuid>')
@login_required
def verify_withdraw(uuid):
	if current_user.user_status == 'admin':
		withdraw = Withdrawals.query.filter_by(uuid=uuid).first()
		withdraw.status = 'paid'
		db.session.commit()
		flash('Updated successfully', 'success')
		return redirect(url_for('admin.withdrawals_list'))
	else:
		abort(404)

@admin.route('/addblogpost', methods=['POST','GET'])
@login_required
def addblogpost():
	if current_user.user_status == 'admin':
			form = AddBlogPostForm()
			if form.validate_on_submit():
				try:
					if form.image.data:
						image_name = save_blog_picture(form.image.data)
					else:
						image_name = 'default_ad_image.png'
					post = Blogpost(title=form.title.data,subject=form.subject.data,image=image_name,post=form.post.data,poster=form.poster.data)
					db.session.add(post)
					db.session.commit()
					flash('Posted successfully', 'success')
					return redirect(url_for('main.blogview'))
				except Exception as e:
					flash(error_message + str(e), 'warning')
					return redirect(url_for('admin.addblogpost'))
			picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
			shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
			return render_template('addblogpost.html', title='Add blog post', form=form)
	else:
		abort(404)

@admin.route('/vmessages', methods=['GET','POST'])
@login_required
def vmessages():
	if current_user.user_status == 'admin':
		page = request.args.get('page', 1, type=int)
		messages = Contact.query.order_by(Contact.id.desc()).paginate(page=page,per_page=10)
		return render_template('vmessages.html', messages=messages, title='Messages')
	else:
		abort(403)

@admin.route('/vmess/<string:message_id>', methods=['GET','POST'])
@login_required
def vmess(message_id):
	if current_user.user_status == 'admin':
		message = Contact.query.get_or_404(message_id)
		message.read = '1'
		db.session.commit()
		return render_template('vmess.html', message=message, title='Message '+message_id)
	else:
		abort(403)

@admin.route('/admindeletemessage/<string:message_id>')
@login_required
def admindeletemessage(message_id):
	if current_user.user_status == 'admin':
		message = Contact.query.filter_by(id=message_id).first()
		db.session.delete(message)
		db.session.commit()
		flash('Message deleted.', 'success')
		return redirect(url_for('admin.vmessages'))
	else:
		abort(403)

@admin.route('/adminusersview', methods=['GET','POST'])
@login_required
def adminusersview():
	if current_user.user_status == 'admin':
		form = BlockedUsersForm()
		page = request.args.get('page', 1, type=int)
		users = User.query.order_by(User.id.desc()).paginate(page=page,per_page=10)
		if form.validate_on_submit():
			users = User.query.filter_by(account_status=form.status.data).order_by(User.id.desc()).paginate(page=page,per_page=10)
		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('adminusersview.html', title='Users view', users=users, shared=len(picked_ads), posted=len(shared_ads), form=form)
	else:
		abort(403)

@admin.route('/vuser/<string:user_id>', methods=['GET','POST'])
@login_required
def vuser(user_id):
	if current_user.user_status == 'admin':
		user = User.query.get_or_404(user_id)
		form = UserEditForm()
		try:
			if form.validate_on_submit():
				user.fullname = form.fullname.data
				user.email = form.email.data
				user.phone = form.phone.data
				user.bank_name = form.bank_name.data
				user.acc_name = form.acc_name.data
				user.acc_number = form.acc_number.data
				user.plan = form.plan.data
				user.balance = form.balance.data
				user.account_status = form.account_status.data
				user.ad_earning = form.ad_earning.data
				user.refer_earning = form.refer_earning.data
				user.user_status = form.user_status.data
				db.session.commit()
				flash('Account updated!', 'success')
				return redirect(url_for('admin.vuser', user_id=user_id))
			elif request.method == 'GET':
				form.fullname.data = user.fullname
				form.email.data = user.email
				form.phone.data = user.phone
				form.bank_name.data = user.bank_name
				form.acc_name.data = user.acc_name
				form.acc_number.data = user.acc_number
				form.plan.data = user.plan
				form.balance.data = user.balance
				form.account_status.data = user.account_status
				form.ad_earning.data = user.ad_earning
				form.refer_earning.data = user.refer_earning
				form.user_status.data = user.user_status
		except Exception as e:
			flash(error_message + str(e), 'warning')
			return redirect(url_for('admin.vuser'))
		return render_template('vuser.html', title='User '+user.fullname, form=form)
	else:
		abort(403)