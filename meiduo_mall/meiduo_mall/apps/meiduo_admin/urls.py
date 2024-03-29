# -*- coding: UTF-8 -*-
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import statistical, users, specifications, images, skus, orders, permissions, groups, admins, spus, options, brands, channels

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
    url(r'^goods/(?P<pk>\d+)/specs/$', skus.SKUView.as_view({'get': 'specs'})),
    # 获取权限类型
    url(r'^permission/content_types/$', permissions.PermissionView.as_view({'get': 'content_type'})),
    # 获取所有权限
    url(r'^permission/simple/$', groups.GroupView.as_view({'get': 'simple'})),
    # 获取所有用户分组
    url(r'^permission/groups/simple/$', admins.AdminView.as_view({'get': 'simple'})),
    # 获取品牌数据
    url(r'^goods/brands/simple/$', spus.SPUView.as_view({'get': 'simple'})),
    # 获取一级分类数据
    url(r'^goods/channel/categories/$', spus.SPUView.as_view({'get': 'category_1'})),
    # 获取二三级分类数据
    url(r'^goods/channel/categories/(?P<pk>\d+)/$', spus.SPUView.as_view({'get': 'category_23'})),
    # 获取商品规格
    url(r'^goods/specs/simple/$', options.OptionView.as_view({'get': 'simple'})),
    # 获取频道分类
    url(r'^goods/categories/$', channels.ChannelView.as_view({'get': 'category'})),
    # 获取频道组
    url(r'^goods/channel_types/$', channels.ChannelView.as_view({'get': 'channel_types'})),
]

# 品牌路由
brands_router = DefaultRouter()
brands_router.register('goods/brands', brands.ChannelView, base_name='brands')
urlpatterns += brands_router.urls

# 商品规格管理路由
specs_router = DefaultRouter()
# specs路由注册
specs_router.register('goods/specs', specifications.SpecsView, base_name='specs')
# specs路由合并
urlpatterns += specs_router.urls

# 频道管理路由
channels_router = DefaultRouter()
channels_router.register('goods/channels', channels.ChannelView, base_name='channels')
urlpatterns += channels_router.urls

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
orders_router.register('orders', orders.OrdersView, base_name='orders')
urlpatterns += orders_router.urls

# 权限管理路由
perms_router = DefaultRouter()
perms_router.register('permission/perms', permissions.PermissionView, base_name='perms')
urlpatterns += perms_router.urls

# 用户组管理路由
groups_router = DefaultRouter()
groups_router.register('permission/groups', groups.GroupView, base_name='groups')
urlpatterns += groups_router.urls

# 管理员管理路由
admin_router = DefaultRouter()
admin_router.register('permission/admins', admins.AdminView, base_name='admins')
urlpatterns += admin_router.urls

# SPU管理路由
spu_router = DefaultRouter()
spu_router.register('goods', spus.SPUView, base_name='spus')
urlpatterns += spu_router.urls

# 规格选项管理路由
option_router = DefaultRouter()
option_router.register('specs/options', options.OptionView, base_name='options')
urlpatterns += option_router.urls


if __name__ == '__main__':
    pass
