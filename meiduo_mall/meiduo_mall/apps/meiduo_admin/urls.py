# -*- coding: UTF-8 -*-
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical

urlpatterns = [
    # 登录
    url(r'^authorizations/$', obtain_jwt_token),
    # 查询用户总数
    url(r'^statistical/total_count/$', statistical.UserCountView.as_view()),


]

if __name__ == '__main__':
    pass
