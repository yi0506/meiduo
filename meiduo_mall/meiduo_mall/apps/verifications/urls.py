# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 图形验证码
    url(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
]


if __name__ == '__main__':
    pass
