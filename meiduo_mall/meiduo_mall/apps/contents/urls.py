# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 首页路由，Django的路由是 头不写尾写
    url(r'^$', views.IndexView.as_view(), name='index'),
    # favicon图片
    url(r'^favicon.ico$', views.FaviconView.as_view()),


]

if __name__ == '__main__':
    pass
