# -*- coding: UTF-8 -*-
from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # 登录
    url(r'^authorizations/$', obtain_jwt_token),
]

if __name__ == '__main__':
    pass
