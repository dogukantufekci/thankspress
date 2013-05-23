from app import db
from app import functions

from app.user.models import User as UserModel, UserProfile as UserProfileModel
from app.email.models import Email as EmailModel

from config import IMAGE_TYPES
from flask.ext.wtf import BooleanField, Email, EqualTo, FileField, HiddenField, \
    Form, Length, PasswordField, Required, TextField


# Registration -----------------------------------

class LoginForm(Form):
    email = TextField("Email", 
        validators = [  Required()])
    password = PasswordField("Password", 
        validators = [  Required()])
    remember_me = BooleanField("Remember Me", 
        default = False)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None
        self.validation_errors = []

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if functions.is_email(self.email.data):
            user = UserModel.login_by_email(self.email.data, self.password.data)
        else:
            user = UserModel.login_by_username(self.email.data, self.password.data)

        if user == None:
            self.validation_errors.append('Email and password did not match.')
            return False
        self.user = user
        return True


class RegisterForm(Form):
    name = TextField("Full Name", 
        validators = [  Required(), 
                        Length( max = 40,    
                                message="Full Name must be maximum 32 characters.")])
    username = TextField("Username", 
        validators = [  Required(),
                        Length( max = 40, 
                                message = "Username must be maximum 320 characters.")])
    email = TextField("Email", 
        validators = [  Required(), 
                        Email(), 
                        Length( max = 320, 
                                message="Email must be maximum 320 characters.")])
    new_password = PasswordField("New Password", 
        validators = [  Required(),
                        Length( min = 8, 
                                max = 40, 
                                message="New Password must be minimum 8 maximum 40 characters."),
                        EqualTo('new_password_again', 
                                message = "New Password did not match the New Password Again field.")])
    new_password_again = PasswordField("New Password Again", 
        validators = [  Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.registered_email = None

    def validate(self):
        rv = Form.validate(self)
        can_register = True

        self.registered_email = EmailModel.get_email_by_email(str(self.email.data))
        if self.registered_email != None and self.registered_email.user != None:
            self.email.errors.append('Email is associated with a registered user.')
            can_register = False

        if not UserModel.is_free_username(str(self.username.data)):
            self.username.errors.append('Username is not available.')
            can_register = False

        if rv and can_register:
            return True
        return False

# Settings -----------------------------------------

class SettingsUserForm(Form):
    username = TextField("Username", 
        validators = [  Required(),
                        Length( max = 40, 
                                message = "Username must be maximum 320 characters.")])

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.user.username == self.username.data or UserModel.is_free_username(self.username.data):
            return True
        self.username.errors.append('Username is not available.')
        return False


class SettingsUserPasswordChangeForm(Form):
    current_password = PasswordField("Current Password", 
        validators = [  Required()])
    new_password = PasswordField("New Password", 
        validators = [  Required(),
                        Length( min = 8, 
                                max = 40, 
                                message="New Password must be minimum 8 maximum 32 characters."),
                        EqualTo('new_password_again', 
                                message = "New Password did not match New Password Again.")])
    new_password_again = PasswordField("New Password Again", 
        validators = [  Required()])

    def __init__(self, user, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = user

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.user.is_users_password(self.current_password.data):
            return True
        self.current_password.errors.append('Current Password field did not match with our records.')
        return False


class SettingsUserProfileForm(Form):
    name = TextField("Name", 
        validators = [  Required(), 
                        Length( max = 40, 
                                message="Name must be maximum 32 characters.")])
    bio = TextField("Bio", 
        validators = [  Length( max = 500, 
                                message="Bio must be maximum 500 characters.")])
    website = TextField("Website", 
        validators = [  Length( max = 500, 
                                message="Website must be maximum 500 characters.")])



class SettingsUserProfilePictureForm(Form):
    picture = FileField("Profile Picture",
        validators = [  Required( message = "Select a picture to upload.")])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        if self.picture.data != None and functions.is_image_type(self.picture.data.filename):
            return True
        self.picture.errors.append('Image files only.')
        return False