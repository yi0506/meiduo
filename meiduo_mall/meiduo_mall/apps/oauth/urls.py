# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 提供qq登录扫码页面
    url(r'^qq/login/$', views.QQAuthURLView.as_view()),
]


if __name__ == '__main__':
    pass
