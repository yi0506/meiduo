# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册： reverse(user:register) == '/register/'
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserNameCountView.as_view()),
]

if __name__ == '__main__':
    pass
