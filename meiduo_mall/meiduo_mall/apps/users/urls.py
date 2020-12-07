# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 用户注册： reverse(user:register) == '/register/'
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$', views.UserNameCountView.as_view()),
    # 判断手机号是否重复注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 实现用户登录逻辑
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 实现退出登录
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 添加邮箱
    url(r'^emails/$', views.EmailView.as_view()),
    # 验证用户邮箱
    url(r'^emails/verification/$', views.VerifyUseEmail.as_view()),
    # 收货地址
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
]

if __name__ == '__main__':
    pass
