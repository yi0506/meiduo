# -*- coding: UTF-8 -*-
# 开发环境配置文件

"""
Django settings for meiduo_mall project.

Generated by 'django-admin startproject' using Django 1.11.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys


# 获取数据库计算机的ip地址
MEIDUO_DB_IP = "192.168.192.133"


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# BASE_DIR：dev.py所在路径的上一层目录的上一层目录下  ---->   xxxx/meiduo/meiduo_mall/meiduo_mall
# BASE_DIR与导包路径无关，导包路径需要参考manage.py的位置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# 添加导包路径
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3r0yqsgm_fcmzi-x+_l7&9qc$3%=xarou96ft08m@k82*bk21o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['www.meiduo.site',
                 '127.0.0.1',
                 'localhost',
                 '172.24.178.15',
                 '172.28.28.187',
                 ]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 因为添加了导包路径，所有可以直接写子应用的模块名
    'users',  # 用户模块
    'contents',  # 首页广告模块
    'verifications',  # 验证码模块，该模块可不用注册，因为即不需要渲染模板，也不需要做模型的迁移
    'oauth',  # 第三方登录认证
    'areas',  # 省市区三级联动
    'goods',  # 商品模块
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

ROOT_URLCONF = 'meiduo_mall.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',  # 配置jinja2模板引擎
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # 配置模板文件加载路径
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # 补充jinja2模板引擎的自定义环境
            'environment': 'meiduo_mall.utils.jinja2_env.jinja2_environment',
        },
    },
]

WSGI_APPLICATION = 'meiduo_mall.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases


# 配置MySQL数据库
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'HOST': MEIDUO_DB_IP,  # 数据库主机
        'PORT': 3306,  # 数据库端口
        'USER': 'yi0506',  # 数据库用户名
        'PASSWORD': '211314',  # 数据库用户密码
        'NAME': 'meiduo'  # 数据库名字
    }
}


# 配置Redis缓存
CACHES = {
    # 默认存储数据库
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/0".format(MEIDUO_DB_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "211314",
        }
    },
    # session数据库
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/1".format(MEIDUO_DB_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "211314",
        }
    },
    # 验证码
    "verify_code": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:6379/2".format(MEIDUO_DB_IP),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "211314",
        }
    },
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"


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
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# 指定加载静态文件的路由前缀，
# 如url为 http://127.0.0.1:8000/static/../../ 类似的都会认为是在访问静态文件
STATIC_URL = '/static/'

# 指定静态文件的加载路径
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# 配置工程日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 指定自定义用户模型类： 值的语法 ----> '子应用.用户模型类'
AUTH_USER_MODEL = 'users.User'

# 自定义用户认证后端
AUTHENTICATION_BACKENDS = ['meiduo_mall.utils.auth_backend.LoginAuthBackend']

# 判断用户是否登录后，指定未登录用户重定向的地址
LOGIN_URL = '/login/'

# QQ登录配置信息
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 邮件SMTP服务器配置信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # 指定邮件后端
EMAIL_HOST = 'smtp.163.com'  # 发邮件主机
EMAIL_PORT = 25  # 发邮件端口
EMAIL_HOST_USER = 'meiduo_yi@163.com'  # 授权的邮箱
EMAIL_HOST_PASSWORD = 'HSUEFCCFKSTYPHLY'  # 邮箱授权时获得的密码，非注册登录密码
EMAIL_FROM = '美多商城<meiduo_yi@163.com>'  # 发件人抬头

# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8000/emails/verification/'

if __name__ == '__main__':
    pass
