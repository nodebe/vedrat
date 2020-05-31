from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from vedrat import app, db
from vedrat.utils import unique_id, save_picture, delete_picture
from vedrat.posts.forms import PostForm, PostSearchForm
from flask_login import current_user, login_required
from vedrat.models import User, Post, PickedPost

posts = Blueprint('posts', __name__)

error_message = 'Error on our side, try again later!'

@posts.route('/reportpost/<string:post_id>')
@login_required
def reportpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	post.report += 1
	if post.report >= 5:
		post.post_status = 'blocked'
	db.session.commit()
	flash('You have reported the post', 'success')
	return redirect(url_for('users.userdashboard'))

@posts.route('/postad', methods=["GET","POST"])
@posts.route('/postad/<string:post_id>', methods=["GET","POST"])
@login_required
def postad(post_id=''):
	form = PostForm()
	if form.validate_on_submit():
		price = (300 * form.posters.data) - 10 * (form.posters.data - 1)
		if post_id=='':
			try:
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
					return redirect(url_for('users.userposts'))
				else:
					flash("You don't have enough balance to complete this action.", 'info')
					return render_template('postad.html', title='Post Ad', form=form)
			except Exception as e:
				flash(error_message, 'warning')
				return redirect(url_for('posts.postad'))
		elif post_id != '':
			try:
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
						previous_picture = post.image
					if form.image.data:
						post.image = save_picture(form.image.data)
					else:
						post.image = 'default_ad_image.png'
					if price_tag == 'remove':
						current_user.balance-=official_price
					elif price_tag == 'add':
						current_user.balance+=official_price
					db.session.commit()
					#delete_picture(previous_picture)
					flash('Your post has been updated successfully', 'success')
					return redirect(url_for('users.userposts'))
				else:
					flash("You don't have enough balance to complete this action.", 'info')
					return render_template('postad.html/post.uuid', title='Post Ad', form=form)
			except Exception as e:
				flash(error_message + str(e), 'warning')
				return redirect(url_for('posts.postad'))
		
	elif request.method == "GET" and post_id!='':
		post = Post.query.filter_by(uuid=post_id).first()
		if post.poster_id == current_user.uuid:
			form.title.data = post.title
			form.link.data = post.link
			form.category.data = post.category
			form.description.data = post.description
			form.posters.data = post.posters_needed
		else:
			abort(403)
	
	picked_ads = PickedPost.query.filter_by(picker_id=current_user.uuid).all()
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('postad.html', title='Post Ad', form=form, shared=len(picked_ads), posted=len(shared_ads))

@posts.route('/usersuspendpost/<string:post_id>')
@login_required
def usersuspendpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	if post.poster_id == current_user.uuid or current_user.user_status == 'admin':
		try:
			post = Post.query.filter_by(uuid=post_id).first()
			if post.post_status == 'open':
				post.post_status = 'suspended'	
				flash("Post suspended and won't be seen by users", 'info')
			elif post.post_status == 'suspended':
				post.post_status = 'open'
				flash("Post opened and can be seen by users", 'info')
			db.session.commit()
		except Exception as e:
			flash(error_message, 'warning')
		finally:
			if current_user.user_status == 'admin':
				return redirect(url_for('admin.adminpostsview'))
			return redirect(url_for('users.userposts'))
	else:
		abort(403)


@posts.route('/userviewpost/<string:post_id>')
@login_required
def userviewpost(post_id):
	post = Post.query.filter_by(uuid=post_id).first()
	return render_template('userviewpost.html', title=post.title, post=post)

@posts.route('/userdeletepost/<string:post_id>')
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
		return redirect(url_for('users.userposts'))
	else:
		abort(403)

@posts.route('/newposts', methods=['GET','POST'])
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

@posts.route('/sharedads')
@login_required
def sharedads():
	page = request.args.get('page', 1, type=int)
	picked_posts = PickedPost.query.filter_by(picker_id=current_user.uuid).order_by(PickedPost.id.desc()).paginate(page=page,per_page=8)
	shared_ads = Post.query.filter_by(poster_id=current_user.uuid).all()
	return render_template('sharedads.html', title='Shared ads', shared=len(picked_posts.items), posted=len(shared_ads), posts=picked_posts)

@posts.route('/ad_post/<string:url>')
def ad_post(url):
    link_ad = PickedPost.query.filter_by(uuid=url).first()
    picker = User.query.filter_by(uuid=link_ad.picker_id).first()
    if link_ad.clicks == 0:
    	picker.ad_earning+=280
    link_ad.clicks+=1
    db.session.commit()
    return redirect(link_ad.main_link)