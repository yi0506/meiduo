# -*- coding: UTF-8 -*-
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter

from .views import statistical, users, specifications, images, skus, orders

urlpatterns = [
    # 登录
    url(r'^authorizations/$', obtain_jwt_token),
    # 查询用户总数
    url(r'^statistical/total_count/$', statistical.UserCountView.as_view()),
    # 日增用户总数
    url(r'^statistical/day_increment/$', statistical.UserDayIncrementView.as_view()),
    # 日活用户总数
    url(r'^statistical/day_active/$', statistical.UserDayActiveView.as_view()),
    # 日下单用户
    url(r'^statistical/day_orders/$', statistical.UserDayOrdersView.as_view()),
    # 一个月内日增用户统计
    url(r'^statistical/month_increment/$', statistical.UserMonthPerDayView.as_view()),
    # 日商品的访问量
    url(r'^statistical/goods_day_views/$', statistical.GoodsDayVisitView.as_view()),
    # 查询用户
    url(r'^users/$', users.UserView.as_view()),
    # 获取SPU商品
    url(r'^goods/simple/$', specifications.SpecsView.as_view({'get': 'simple'})),
    # 获取sku商品
    url(r'^skus/simple/$', images.ImagesView.as_view({'get': 'simple'})),
    # 获取spu商品规格及规格选项
    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SKUView.as_view({'get': 'specs'}))
]

# 商品规格管理路由
specs_router = DefaultRouter()
# specs路由注册
specs_router.register('goods/specs', specifications.SpecsView, base_name='specs')
# specs路由合并
urlpatterns += specs_router.urls

# 图片管理路由
images_router = DefaultRouter()
images_router.register('skus/images', images.ImagesView, base_name='images')
urlpatterns += images_router.urls

# sku管理路由
skus_router = DefaultRouter()
skus_router.register('skus', skus.SKUView, base_name='skus')
urlpatterns += skus_router.urls

# orders管理路由
orders_router = DefaultRouter()
orders_router.register('orders', orders.OrdersView, base_name='orders管理路由')
urlpatterns += orders_router.urls


if __name__ == '__main__':
    pass
