# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 用户注册： reverse(user:register) == '/register/'
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
]

if __name__ == '__main__':
    pass
