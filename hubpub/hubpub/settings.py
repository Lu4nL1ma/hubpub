from pathlib import Path
import os

# 1. BASE_DIR - Localização raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. CONFIGURAÇÕES DE SEGURANÇA (Valores diretos no código)
SECRET_KEY = 'django-insecure-swlfypx8o#*1y$**q7li-o0fu^(-p1@p82(qyx^k&3i0&3!ud%'

DEBUG = True

ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', '.pythonanywhere.com']

# 3. DEFINIÇÃO DE APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_hubpub',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hubpub.urls'

# 4. CONFIGURAÇÃO DE TEMPLATES (Ajustado para DIRS não ficar vazio)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hubpub.wsgi.application'

# 5. BANCO DE DADOS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 6. INTERNACIONALIZAÇÃO
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 7. ARQUIVOS ESTÁTICOS E MÍDIA
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')] if os.path.exists(os.path.join(BASE_DIR, 'static')) else []

MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 8. CORREÇÃO CSRF (Trusted Origins)
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
    'https://*.pythonanywhere.com',
]

# 9. REDIRECIONAMENTOS
LOGIN_REDIRECT_URL = '/staff/' 
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# 10. CREDENCIAIS META (Para consulta se necessário)
PAGE_ACCESS_TOKEN = 'EAAUB01Agx2YBQza2bbgTBeFh7WlDy93fs6UabSLr5Kp9uwyyqfHpAXnNpOEmZADshM1tweiZCPoSkJ1PnKdDhYnvu3pJfFmQHwAlg6Wr8Pz5EecUIfJghYAXQvermuRDiITE0YeBarWiCngZBPyY7zCvLSPJcZBVklnRWJII3p5Ab4GaIORYy550SxsSYNvCKRuM6Ds5'
FACEBOOK_PAGE_ID = '1044548165403490'
INSTA_BUSINESS_ID = '17841467620559548'
BASE_URL_PUBLICA = 'https://infinitycursos.site/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'