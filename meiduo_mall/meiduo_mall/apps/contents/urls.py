# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 首页广告， 路由为'/' 但是不需要写，因为根路径'/'会被django自动去除后，进行路由匹配
    # 如果写成 r'^/$，那么路由就要写 http://127.0.0.1:8000// ，两个斜杠
    url(r'^$', views.IndexView.as_view(), name='index'),

]

if __name__ == '__main__':
    pass
