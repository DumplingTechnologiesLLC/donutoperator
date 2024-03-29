"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
# import django_heroku


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET", None)

# SECURITY WARNING: don't run with debug turned on in production!
debug_val = os.environ.get("DEBUG", True)
DEBUG = (type(debug_val) is str and debug_val == "True") or (
    type(debug_val) is bool and debug_val)
local_val = os.environ.get("LOCAL", False)
LOCAL = (type(local_val) is str and local_val == "True") or (
    type(local_val) is bool and local_val)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    "www.peoplekilledbypolice.com",
    "donutoperator.herokuapp.com",
    "staging-donut-operator.herokuapp.com",
    'www.bodycamdatabase.com',
    'bodycamdatabase.com',
]

PAGE_SIZE = int(os.environ.get("PAGE_SIZE", 25))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    # 'bodycams',
    'videos',
    'robots',
    'feedback',
    # "rules",
    # 'storages',
    "captcha",
    'corsheaders',
    "rest_framework",
    'rules.apps.AutodiscoverRulesConfig',
]
if not DEBUG and not LOCAL:
    INSTALLED_APPS += ['storages']

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'videos.context_processors.supply_basic_data',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LOGOUT_REDIRECT_URL = '/'
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases
if LOCAL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    import dj_database_url
    database_url = os.environ.get("DATABASE_URL", None)
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            ssl_require=True
        )
    }
    # DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# AWS Static File Storage

AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", None)
AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", None)
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = None

STATIC_URL = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)
if DEBUG and LOCAL:
    STATIC_URL = '/static/'

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
if not DEBUG and not LOCAL:
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'config.storage_backends.MediaStorage'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static'),
)
SITE_ID = 1

TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 1120,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'plugins': '''
            textcolor save link image media preview codesample contextmenu
            table code lists fullscreen  insertdatetime  nonbreaking
            contextmenu directionality searchreplace wordcount visualblocks
            visualchars code fullscreen autolink lists  charmap print  hr
            anchor pagebreak
            ''',
    'toolbar1': '''
            fullscreen preview bold italic underline | fontselect,
            fontsizeselect  | forecolor backcolor | alignleft alignright |
            aligncenter alignjustify | indent outdent | bullist numlist table |
            | link image media | codesample |
            ''',
    'toolbar2': '''
            visualblocks visualchars |
            charmap hr pagebreak nonbreaking anchor |  code |
            ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}
# FILEBROWSER SETTINGS
FILEBROWSER_DIRECTORY = "media"

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = "login/"
SECURE_SSL_REDIRECT = False
if not DEBUG and not LOCAL:
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = [
        # r'^$',
        # r'^(?P<date>[0-9]+)$',
        # r'^news/$',
        # r'^bodycams$',
        # r'^bodycams/(?P<date>[0-9]+)$',
    ]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = False

# this is incompatible with Boto3
# django_heroku.settings(locals())


def get_cache():
    import os
    try:
        servers = os.environ['MEMCACHIER_SERVERS']
        username = os.environ['MEMCACHIER_USERNAME']
        password = os.environ['MEMCACHIER_PASSWORD']
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
                # TIMEOUT is not the connection timeout! It's the default expiration
                # timeout that should be applied to keys! Setting it to `None`
                # disables expiration.
                'TIMEOUT': None,
                'LOCATION': servers,
                'OPTIONS': {
                    'binary': True,
                    'username': username,
                    'password': password,
                    'behaviors': {
                        # Enable faster IO
                        'no_block': True,
                        'tcp_nodelay': True,
                        # Keep connection alive
                        'tcp_keepalive': True,
                        # Timeout settings
                        'connect_timeout': 2000,  # ms
                        'send_timeout': 750 * 1000,  # us
                        'receive_timeout': 750 * 1000,  # us
                        '_poll_timeout': 2000,  # ms
                        # Better failover
                        'ketama': True,
                        'remove_failed': 1,
                        'retry_timeout': 2,
                        'dead_timeout': 30,
                    }
                }
            }
        }
    except:  # noqa: E722
        return {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
            }
        }
    # return {
    #     'default': {
    #         "BACKEND": "django.core.cache.backends.db.DatabaseCache",
    #         "LOCATION": "shooting_cache_table"
    #     }
    # }


CACHES = get_cache()
ROBOTS_SITEMAP_URLS = [
    'https://www.peoplekilledbypolice.com/sitemap.xml',
    'bodycamdatabase.com/sitemap.xml',
]
if LOCAL:
    ROBOTS_SITEMAP_URLS = [
        'localhost:8000/sitemap.xml',
    ]
