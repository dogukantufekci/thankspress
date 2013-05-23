from flask import render_template
from config import ADMINS
from flask.ext.mail import Message
from app import mail
from decorators import async

@async
def send_async_email(msg):
	mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = text_body
	msg.html = html_body
	send_async_email(msg)

def follower_notification(follower, followed):
    send_email("%s is now following you." % follower.username,
        ADMINS[0],
        [followed.primary_email.email],
        render_template("emails/follower_notification.txt", 
            user = followed, follower = follower),
        render_template("emails/follower_notification.html", 
            user = followed, follower = follower))

def register(email):
    send_email("Welcome to ThanksPress!",
        ADMINS[0],
        [email.email],
        render_template("emails/register.txt", 
            email = email),
        render_template("emails/register.html", 
            email = email))

def settings_emails_email_add(email):
    send_email("New Email Added.",
        ADMINS[0],
        [email.email],
        render_template("emails/settings_emails_email_add.txt", 
            email = email),
        render_template("emails/settings_emails_email_add.html", 
            email = email))

# def settings_emails_email_delete(email):
#     send_email("ThanksPress email verification.",
#         ADMINS[0],
#         [email.email],
#         render_template("emails/email_verification.txt", 
#             email = email),
#         render_template("emails/email_verification.html", 
#             email = email))

# def settings_emails_email_make_primary(email):
#     send_email("ThanksPress email verification.",
#         ADMINS[0],
#         [email.email],
#         render_template("emails/email_verification.txt", 
#             email = email),
#         render_template("emails/email_verification.html", 
#             email = email))

def settings_emails_email_send_key(email):
    send_email("Email Verification Key.",
        ADMINS[0],
        [email.email],
        render_template("emails/settings_emails_email_send_key.txt", 
            email = email),
        render_template("emails/settings_emails_email_send_key.html", 
            email = email))