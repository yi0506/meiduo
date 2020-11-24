# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # Django的路由是 头不写尾写
    url(r'^$', views.IndexView.as_view(), name='index'),

]

if __name__ == '__main__':
    pass
