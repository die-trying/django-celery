import environ

root = environ.Path(__file__) - 3        # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env()                   # reading .env file

SITE_ROOT = root()

USE_L10N = True
USE_i18N = True

LANGUAGE_CODE = 'EN'

DEBUG = env('DEBUG')    # False if not in os.environ

DATABASES = {
    'default': env.db(),    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}

INSTALLED_APPS = [
    'elk',
    'crm',
    'lessons',
    'products',
    'hub',
    'timeline',
    'acc',

    'django_countries',
    'django_markdown',

    'social.apps.django_app.default',
    'django_nose',
    'django_admin_bootstrapped',
    'django.contrib.admindocs',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'debug_toolbar',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
]
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--nologcapture'
]

ROOT_URLCONF = 'elk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',

                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
            ],
        },
    },
]

DAB_FIELD_RENDERER = 'django_admin_bootstrapped.renderers.BootstrapFieldRenderer'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'social.backends.google.GoogleOAuth2',
    'social.backends.facebook.FacebookOAuth2',
)
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'acc.pipelines.save_profile_picture'

)
SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

WSGI_APPLICATION = 'elk.wsgi.application'

public_root = root.path('public/')

MEDIA_ROOT = env('MEDIA_ROOT')
MEDIA_URL = 'media/'

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')

SECRET_KEY = env('SECRET_KEY')  # Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ


CACHES = {
    'default': env.cache(),
}
