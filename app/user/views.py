from flask import render_template, flash, redirect, url_for, g, session, request
from flask.ext.login import current_user, login_user, login_required, logout_user

from app import app, db, lm
from app.emails import email_verification, follower_notification
from app.user.forms import ChangePasswordForm, EditProfileForm, EmailForm, \
    PickUsernameForm, SettingsForm, SignInForm, SignUpForm, SearchForm
from app.user.models import Email, Follow, User, UserProfile
from app.functions import Functions

@lm.user_loader
def load_user(id):
    return User.get_user(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.update_date_last_acted()
        db.session.add(g.user)
        db.session.commit()
        if g.user.is_activated():
            pass
        elif g.user.is_new():
            form = PickUsernameForm()
            if form.validate_on_submit():
                g.user.username = form.username.data
                g.user.make_activated()
                db.session.add(g.user)
                db.session.commit()
                flash('Welcome to ThanksPress!')
                return redirect(url_for('user_timeline', username = g.user.username))
            else:
                return render_template('user/account_pick_username.html',
                    form = form,
                    title = 'Pick Username')
        elif g.user.is_deactivated():
            g.user.make_activated()
            db.session.add(g.user)
            db.session.commit()
            flash('Great to see you back!')

@app.route('/account/change-password', methods = ['GET', 'POST'])
@app.route('/account/change-password/', methods = ['GET', 'POST'])
@login_required
def account_change_password():
    form = ChangePasswordForm(g.user)
    if form.validate_on_submit():
        g.user.change_password(form.new_password.data)
        db.session.add(g.user)
        db.session.commit()
        flash('You have successfully changed your password.')
    return render_template("user/account_change_password.html",
        form = form,
        title = "Change Password")

@app.route('/account/deactivate', methods = ['GET','POST'])
@app.route('/account/deactivate/', methods = ['GET','POST'])
@login_required
def account_deactivate():
    form = SignInForm()
    if form.validate_on_submit():
        form.user.make_deactivated()
        db.session.add(form.user)
        db.session.commit()
        return sign_out()
    return render_template('user/account_deactivate.html',
        form = form,
        title = 'Deactivate Account')

@app.route('/account/edit-profile', methods = ['GET', 'POST'])
@app.route('/account/edit-profile/', methods = ['GET', 'POST'])
@login_required
def account_edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        g.user.profile.name = form.name.data
        g.user.profile.bio = form.bio.data
        g.user.profile.facebook_username = form.facebook_username.data
        g.user.profile.is_facebook_visible = form.is_facebook_visible.data
        g.user.profile.twitter_username = form.twitter_username.data
        g.user.profile.is_twitter_visible = form.is_twitter_visible.data
        g.user.profile.website = form.website.data
        db.session.add(g.user.profile)
        db.session.commit()
        flash('Changes have been saved.')
        return redirect(url_for('account_edit_profile'))
    else:
        form.name.data = g.user.profile.name
        form.bio.data = g.user.profile.bio
        form.facebook_username.data = g.user.profile.facebook_username
        form.is_facebook_visible.data = g.user.profile.is_facebook_visible
        form.twitter_username.data = g.user.profile.twitter_username
        form.is_twitter_visible.data = g.user.profile.is_twitter_visible
        form.website.data = g.user.profile.website
    return render_template('user/account_edit_profile.html',
        form = form,
        title = 'Account Settings for' + g.user.username)

@app.route('/account/manage-emails', methods = ['GET', 'POST'])
@app.route('/account/manage-emails/', methods = ['GET', 'POST'])
@login_required
def account_manage_emails():
    form = EmailForm()
    if form.validate_on_submit():
        return redirect(url_for('account_manage_emails_add', email = form.email.data))
    return render_template('user/account_manage_emails.html',
        form = form, 
        title = 'Manage Emails')

@app.route('/account/manage-emails/add/<email>/')
@login_required
def account_manage_emails_add(email = None):
    if email != None and Functions.is_email(email):
        email_object = Email.get_email_by_email(email)
        if email_object == None:
            email = Email(email = email, user_id = g.user.id)
            db.session.add(email)
            db.session.commit()
            email_verification(email)
            flash('%s has been successfully added.' % (email.email)) 
        else:
            if email_object.user == g.user:
                flash('%s is already added.' % (email_object.email)) 
            else:
                flash('%s registered by another user.' % (email_object.email)) 
    return redirect(url_for('account_manage_emails'))

@app.route('/account/manage-emails/delete/<email>/')
@login_required
def account_manage_emails_delete(email = None):
    if email != None and Functions.is_email(email):
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be deleted.')
        elif email not in g.user.emails:
            flash('%s is not your email. You cannot delete it.' % (email.email)) 
        elif email.is_primary:
            flash('%s is your primary email. It cannot be deleted.' % (email.email))
        else:
            email.make_deleted()
            db.session.add(email)
            db.session.commit()
            flash('%s has been successfully deleted.' % (email.email))
    return redirect(url_for('account_manage_emails'))

@app.route('/account/manage-emails/make-primary/<email>/')
@login_required
def account_manage_emails_make_primary(email = None):
    if email != None and Functions.is_email(email):
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be primary email.')
        elif email not in g.user.emails:
            flash('%s is not registered by your account.' % (email.email))
        elif email.is_primary:
            flash('%s is already your primary email.' % (email.email))
        elif email.is_not_verified():
            flash('%s is not a verified email. Please verify to make primary.' % (email.email))
        else:
            current_primary_email = g.user.get_primary_email()
            current_primary_email.is_primary = False
            db.session.add(current_primary_email)
            email.make_primary()
            db.session.add(email)
            db.session.commit()
            flash('%s has been successfully made your primary email.' % (email.email))
    return redirect(url_for('account_manage_emails'))

@app.route('/account/manage-emails/request-key/<email>/')
@login_required
def account_manage_emails_request_key(email = None):
    if email == None or not Functions.is_email(email):
        pass
    else:
        email = Email.get_email_by_email(email)
        if email == None:
            pass
        elif email not in g.user.emails:
            pass
        elif email.is_not_verified():
            email_verification(email)
            flash('We sent your email verification to %s. Please check your inbox for verification instructions.' % (email.email))
        elif email.is_verified():
            flash('%s is already verified.' % (email.email))
        elif email.is_reported():
            flash('%s is reported. It cannot be verified until case is resolved.' % (email.email))
    return redirect(url_for('account_manage_emails'))

@app.route('/account/manage-emails/verify/<email>/')
@login_required
def account_manage_emails_verify(email = None):
    if email == None or not Functions.is_email(email):
        pass
    elif request.args.get("key") == None or len(request.args.get("key")) != 32:
        flash('Verification key could not be detected. You may have a broken link.')
    else:
        email = Email.get_email_by_email(email)
        if email == None:
            flash('Unregistered email cannot be verified.')
        elif email not in g.user.emails:
            flash('%s is not your email. If you own this email, please send an email to \'emails@thankspress.com\'' % (email.email)) 
        elif email.is_verified():
            flash('%s is already verified.' % (email.email))
        elif email.is_reported():
            flash('%s is reported. It cannot be verified until case is resolved.' % (email.email))
        else:
            if email.verification_key == request.args.get("key"):
                email.make_verified()
                db.session.add(email)
                db.session.commit()
                flash('%s has been successfully verified.' % (email.email))
            else:
                flash('Verification key is not valid. Please request a new verification key and try again.')
    return redirect(url_for('account_manage_emails'))

@app.route('/account', methods = ['GET', 'POST'])
@app.route('/account/', methods = ['GET', 'POST'])
@app.route('/account/settings', methods = ['GET', 'POST'])
@app.route('/account/settings/', methods = ['GET', 'POST'])
@login_required
def account_settings():
    form = SettingsForm(g.user)
    if form.validate_on_submit():
        g.user.username = form.username.data
        db.session.add(g.user)
        db.session.commit()
        flash('Changes have been saved.')
        return redirect(url_for('account_settings'))
    else:
        form.username.data = g.user.username
    return render_template('user/account_settings.html',
        form = form,
        title = 'Account Settings for' + g.user.username)

@app.route('/follow/<int:followed_id>/')
@login_required
def follow(followed_id):
    user = User.get_user(followed_id)
    if user != None and not user.is_deleted():
        if not Follow.is_following_by_follower_and_followed(g.user.id, user.id):
            follow = Follow(g.user.id, user.id)
            db.session.add(follow)
            db.session.commit()
            follower_notification(g.user, user)
        return redirect(url_for('user_timeline', username = user.username))
    return render_template('404.html'), 404

@app.route('/unfollow/<int:followed_id>/')
@login_required
def unfollow(followed_id):
    user = User.get_user(followed_id)
    if user != None and not user.is_deleted():
        follow = Follow.get_follow_by_follower_and_followed(g.user.id, user.id)
        if follow != None:
            follow.make_deleted()
            db.session.add(follow)
            db.session.commit()
        return redirect(url_for('user_timeline', username = user.username))
    return render_template('404.html'), 404

@app.route('/sign-in', methods = ['GET', 'POST'])
@app.route('/sign-in/', methods = ['GET', 'POST'])
def sign_in():
    if g.user.is_authenticated():
        flash("You are already registered.")
        return redirect(url_for('user_timeline', username = g.user.username))
    form = SignInForm()
    if form.validate_on_submit():
            login_user(form.user, remember = form.remember_me.data)
            return redirect(request.args.get("next") or url_for('timeline'))
    return render_template('user/sign_in.html',
        form = form,
        title = 'Sign In',
        message = '/sign-in')

@app.route('/sign-out')
@app.route('/sign-out/')
def sign_out():
    logout_user()
    return redirect(url_for('timeline'))

@app.route('/sign-up', methods = ['GET', 'POST'])
@app.route('/sign-up/', methods = ['GET', 'POST'])
def sign_up():
    if g.user.is_authenticated():
        flash("You are already registered.")
        return redirect(url_for('user_timeline', username = g.user.username))
    form = SignUpForm()
    if form.validate_on_submit():
        #Register user's Account
        user = User(password = form.password.data)
        db.session.add(user)
        db.session.commit()
        #Register user's Profile
        user_profile = UserProfile(user_id = user.id, name = form.name.data)
        db.session.add(user_profile)
        #Register user's Email
        email = Email(user_id = user.id, email = form.email.data, is_primary = True)
        db.session.add(email)
        #Follow user's self
        follow = Follow(follower_id = user.id, followed_id = user.id)
        db.session.add(follow)
        db.session.commit()
        #Redirect to Sign In
        flash('You have successfully signed up for ThanksPress.')
        return redirect(url_for('sign_in'))
    return render_template('user/sign_up.html',
        form = form,
        title = 'Sign Up',
        message = "/sign-up")

@app.route('/')
@app.route('/timeline')
@app.route('/timeline/')
def timeline():
    return render_template('user/timeline.html',
        title = 'Timeline',
        message = '/timeline')

@app.route('/<username>/followers')
@app.route('/<username>/followers/')
def user_followers(username = None):
    if username != None:
        user = User.get_user_by_username(username)
        if user != None and user.is_active():
            return render_template('user/user_followers.html', 
                title = 'They are following' + user.username,
                message = '/' + user.username + '/followers')
    return render_template('404.html'), 404

@app.route('/<username>/following')
@app.route('/<username>/following/')
def user_following(username = None):
    if username != None:
        user = User.get_user_by_username(username)
        if user != None and user.is_active():
            return render_template('user/user_following.html', 
                title = user.username + ' is following them.',
                message = '/' + user.username + '/following')
    return render_template('404.html'), 404

@app.route('/<username>/thanks-given')
@app.route('/<username>/thanks-given/')
def user_thanks_given(username = None):
    if username != None:
        user = User.get_user_by_username(username)
        if user != None and user.is_active():
            return render_template('user/user_thanks_given.html', 
                title = 'Thanks Given by' + user.username,
                message = '/' + user.username + '/thanks-given')
    return render_template('404.html'), 404

@app.route('/<username>')
@app.route('/<username>/')
@app.route('/<username>/timeline')
@app.route('/<username>/timeline/')
def user_timeline(username = None):
    user = User.get_user_by_username(username)
    if user != None and user.is_active():
        return render_template('user/user_timeline.html',
            Follow = Follow,
            user = user,
            title = user.username + "'s Timeline")
    return render_template('404.html'), 404

# @app.route('/account/activate', methods = ['GET','POST'])
# @login_required
# def account_activate():
#     form = ActivateUserForm()
#     if g.user.is_deactivated():
#         return
#     g.user.make_user_active()
#     db.session.add(g.user)
#     db.session.commit()
#     return redirect("/index")

# @app.route('/settings/deactivate')
# @login_required
# def settings_deactivate():
#     return redirect("/index")

# @app.route('/settings/delete')
# @login_required
# def settings_delete():
#     return redirect("/index")

# @app.route('/edit-profile')
# @login_required
# def edit_profile():
#     return render_template("user/edit_profile.html",
#         title = "Edit Profile")

# @app.route('/manage-emails')
# @login_required
# def manage_emails():
#     return render_template("user/settings.html",
#         title = "Settings",
#         message = "Hello world")

# @app.route('/account/reset-password')
# def reset_password():
#     return render_template("user/account_reset_password.html",
#         title = "Reset Password",
#         message = "Hello world")

# @app.route('/account/activity-log')
# @login_required
# def account_activity_log():
#     return render_template("user/account_activity_log.html", 
#         title = "Activity Log")

@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('user/500.html'), 500