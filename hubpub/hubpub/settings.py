from pathlib import Path
import os

# 1. BASE_DIR - Localização raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. CONFIGURAÇÕES DE SEGURANÇA
SECRET_KEY = 'django-insecure-swlfypx8o#*1y$**q7li-o0fu^(-p1@p82(qyx^k&3i0&3!ud%'

DEBUG = True # Mantenha True enquanto estiver configurando, mude para False depois.

ALLOWED_HOSTS = ['lu4nl1ma.pythonanywhere.com', 'localhost', '127.0.0.1']

# 3. DEFINIÇÃO DE APPS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_hubpub', # Seu app principal
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

# 4. CONFIGURAÇÃO DE TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], 
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

# 5. BANCO DE DADOS (Configurado para MySQL do PythonAnywhere)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'Lu4nL1ma$app_hubpub',      # Nome que você criou na aba Databases
        'USER': 'Lu4nL1ma',                # Seu usuário do PythonAnywhere
        'PASSWORD': '123lux456',      # A senha que você definiu para o BANCO
        'HOST': 'Lu4nL1ma.mysql.pythonanywhere-services.com', 
        'PORT': '3306',
    }
}

# 6. INTERNACIONALIZAÇÃO
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 7. ARQUIVOS ESTÁTICOS E MÍDIA
STATIC_URL = '/static/'

# MUDANÇA: O ROOT deve apontar para uma pasta de DESTINO (ex: staticfiles)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# MUDANÇA: O DIRS deve apontar para a pasta de ORIGEM (static)
# Se você tiver uma pasta 'static' na raiz do projeto, use assim:
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 8. CORREÇÃO CSRF (Trusted Origins)
CSRF_TRUSTED_ORIGINS = [
    'https://lu4nl1ma.pythonanywhere.com',
]

# 9. REDIRECIONAMENTOS
LOGIN_REDIRECT_URL = '/staff/' 
LOGOUT_REDIRECT_URL = '/login/'
LOGIN_URL = '/login/'

# 10. CREDENCIAIS META
PAGE_ACCESS_TOKEN = 'EAAUB01Agx2YBQza2bbgTBeFh7WlDy93fs6UabSLr5Kp9uwyyqfHpAXnNpOEmZADshM1tweiZCPoSkJ1PnKdDhYnvu3pJfFmQHwAlg6Wr8Pz5EecUIfJghYAXQvermuRDiITE0YeBarWiCngZBPyY7zCvLSPJcZBVklnRWJII3p5Ab4GaIORYy550SxsSYNvCKRuM6Ds5'
FACEBOOK_PAGE_ID = '1044548165403490'
INSTA_BUSINESS_ID = '17841467620559548'
BASE_URL_PUBLICA = 'https://infinitycursos.site/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'