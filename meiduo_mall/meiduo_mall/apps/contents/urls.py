# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 首页广告， 路由为'/' 但是不需要写，因为根路径'/'会自动补充
    url(r'^$', views.IndexView.as_view(), name='index'),

]

if __name__ == '__main__':
    pass
