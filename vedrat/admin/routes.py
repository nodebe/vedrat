from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from vedrat import app, db
from vedrat.utils import unique_id
from vedrat.admin.forms import FAQForm
#from passlib.hash import sha256_crypt as sha256
from flask_login import login_user, current_user, login_required
from vedrat.models import FAQ, Withdrawals, PickedPost, Post

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
			flash(error_message + str(e), 'warning')
			return redirect(url_for('users.userdashboard'))
	else:
		abort(404)

@admin.route('/withdrawals_list')
@login_required
def withdrawals_list():
	if current_user.user_status == 'admin':
		page = request.args.get('page', 1, type=int)
		withdrawals = Withdrawals.query.order_by(Withdrawals.id.desc()).paginate(page=page,per_page=10)
		picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
		shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
		return render_template('withdrawals_list.html', title='Withdrawals', shared=len(picked_ads), posted=len(shared_ads),withdrawals=withdrawals)
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

'''
@admin.route('/vmessage', methods=['GET','POST'])
@login_required
def vmessages():
	if current_user.user_status == 'admin':
		messages = Contact.query.all()
		return render_template('vmessages.html', messages=messages)
	else:
		abort(403)

@admin.route('/vmess/<string:uuid>', methods=['GET','POST'])
@login_required
def vmess(uuid):
	if current_user.user_status == 'admin':
		message = Contact.query.filter_by(uuid=uuid).first()
		message.read = 1
		db.session.commit()
		return render_template('vmess.html', message=message)
	else:
		abort(403)
		'''