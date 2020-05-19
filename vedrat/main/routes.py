import flask
from flask import Blueprint, render_template, url_for, flash, redirect, request, session
from vedrat import app, db
from vedrat.main.forms import ContactForm
from flask_login import current_user
from vedrat.models import Contact, Post, FAQ

main = Blueprint('main', __name__)

error_message = 'Error on our side, try again later!'

@main.route('/')
@main.route('/index')
def index():
	popular_posts = Post.query.order_by(Post.posters_applied.desc()).limit(4).all()
	new_posts = Post.query.order_by(Post.id.desc()).limit(4).all()

	return render_template('index.html', title='Home', popular_posts=popular_posts, new_posts=new_posts)

@main.route('/index/<string:referrer_id>')
def index_referrer(referrer_id):
	session['referrer_id'] = referrer_id
	return redirect(url_for('main.index'))

@main.route('/faq')
def faq():
	faqs = FAQ.query.all()
	return render_template('faq.html', title='Frequently Asked Questions',faqs=faqs)

@main.route('/contact', methods=['GET','POST'])
def contact():
	form = ContactForm()
	if current_user.is_authenticated:
		if request.method == 'GET':
			form.fullname.data = current_user.fullname
			form.email.data = current_user.email
	try:
		if form.validate_on_submit():
			contact = Contact(fullname=form.fullname.data,email=form.email.data,subject=form.subject.data,message=form.message.data)
			db.session.add(contact)
			db.session.commit()
			flash('Your message has been posted successfully. We will get back to you through an email message', 'success')
			return redirect(url_for('main.contact'))
	except Exception as e:
		flash(error_message, 'warning')
	return render_template('contact.html', title='Contact', form=form)
