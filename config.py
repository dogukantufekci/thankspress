import os

# Admins
ADMINS = ('thankspress@creco.co',)

# Apps
APPS = ('email', 'follow', 'media', 'notification', 'public_page', 'thank', 'user',)

# Directories
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Email Server
MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'thankspress@creco.co'
MAIL_PASSWORD = 'donothack'

# Forbidden usernames due to reserved site specific URI
FORBIDDEN_USERNAMES = ('account', 'pages', 'public-pages', 'sign-in', 'sign-up', \
    'sign-out','thankspress','timeline','users',)

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASEDIR, 'db_repository')

# Upload
UPLOAD_FOLDER = os.path.join(BASEDIR, 'media_uploads')
IMAGE_TYPES = tuple('jpg jpe jpeg png gif svg bmp'.split())

# WTF
CSRF_ENABLED = True
SECRET_KEY = 'thankspress'
