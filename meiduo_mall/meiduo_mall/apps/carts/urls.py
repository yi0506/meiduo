# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # 购物车管理
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    # 全选购物车
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view()),
]

if __name__ == '__main__':
    pass
