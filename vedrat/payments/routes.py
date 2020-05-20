from flask import Blueprint, render_template, url_for, flash, redirect, request
from vedrat import app, db
from vedrat.utils import unique_id, referral_earning, date_compare
from vedrat.payments.forms import DepositForm
from flask_login import current_user, login_required
from vedrat.models import User, Withdrawals
from datetime import datetime as dt
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction

payments = Blueprint('payments', __name__)

paystack_secret_key = 'sk_test_37408e2ede43f221bed5b6ab0d7ed78913f2b6dc'
paystack = Paystack(secret_key = paystack_secret_key)

error_message = 'Error on our side, try again later!'

@payments.route('/pay_plan_<string:plan_id>')
@login_required
def pay_plan(plan_id):
	if current_user.plan == '0':
		try:
			transaction_id = plan_id.upper()+'_'+current_user.uuid+'_'+unique_id()
			current_user.verify_id_code = transaction_id
			db.session.commit() 
			if plan_id == 'a':
				response = Transaction.initialize(reference=transaction_id,amount=300000, email=current_user.email)
				return redirect(response['data']['authorization_url'])
			elif plan_id == 'b':
				response = Transaction.initialize(reference=transaction_id,amount=500000, email=current_user.email)
				return redirect(response['data']['authorization_url'])
		except Exception as e:
			flash('Please check your internet connection!', 'warning')
			return redirect('userpayment')
	else:
		flash('You are already subscribed to a plan ' + str(current_user.plan), 'warning')
		return redirect('userpayment')

@payments.route('/verify_transaction')
@login_required
def verify_transaction():
	try:
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
			return redirect(url_for('users.userdashboard'))
		else:
			flash('Your subscription was not successful!', 'info')
			return redirect(url_for('payments.userpayment'))
	except Exception as e:
		flash(error_message, 'warning')
		return redirect(url_for('users.userdashboard'))

@payments.route('/wb_deposit', methods=['POST'])
@login_required
def wb_deposit():
	form = DepositForm()
	if form.validate_on_submit():
		try:
			transaction_id = 'WB'+'_'+current_user.uuid+'_'+unique_id()
			current_user.verify_id_code = transaction_id
			db.session.commit()
			response = Transaction.initialize(reference=transaction_id,amount=form.amount.data*100, email=current_user.email)
			return redirect(response['data']['authorization_url'])
		except Exception as e:
			flash('Please check your internet connection!', 'warning')
			return redirect(url_for('payments.userpayment'))
	else:
		flash('Deposit not approved', 'warning')
		return redirect(url_for('payments.userpayment'))

@payments.route('/withdraw_balance')
@login_required
def withdraw_balance():
	try:
		if current_user.date_of_payment != None:
			withdraw_date = date_compare()
			new_date = dt.now().strftime('%Y-%m-%d')
			if current_user.bank_name!='' and current_user.acc_name!='' and current_user.acc_number!='':
				if new_date >= withdraw_date:
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
					return redirect(url_for('payments.userpayment'))
				else:
					d1 = dt.strptime(withdraw_date, '%Y-%m-%d')
					d2 = dt.strptime(new_date, '%Y-%m-%d')
					flash('You have {} more days till you can make a withdrawal '.format(abs((d1-d2).days)), 'info')
					return redirect(url_for('payments.userpayment'))
			else:
				flash('Please update your bank information', 'info')
				return redirect(url_for('users.usersettings'))
		else:
			flash('You have to be subscribed to a plan', 'info')
			return redirect(url_for('payments.userpayment'))
	except Exception as e:
		flash(error_message, 'warning')
		return redirect(url_for('payments.userpayment'))

@payments.route('/userpayment')
def userpayment():
	if current_user.is_authenticated:
		form = DepositForm()
		refer_balance = referral_earning()
		
		return render_template('userpayment.html', title='Payment',refer_balance=refer_balance, form=form)
	else:
		return render_template('userpayment.html', title='Payment')
