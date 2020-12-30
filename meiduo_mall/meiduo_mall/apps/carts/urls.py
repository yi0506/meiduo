# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    # 购物车管理
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
    # 全选购物车
    url(r'^carts/selection/$', views.CartsSelectAllView.as_view()),
    # 展示简单购物车（首页、商品列表页、商品详情页的购物车展示）
    url(r'^carts/simple/$', views.CartsSimpleView.as_view()),
]

if __name__ == '__main__':
    pass
