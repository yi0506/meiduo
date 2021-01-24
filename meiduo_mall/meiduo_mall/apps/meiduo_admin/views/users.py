# -*- coding: UTF-8 -*-
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.users import UserSerializer
from meiduo_mall.utils.DRF_paginator import UserPaginator
from users.models import User


class UserView(ListAPIView):
    """获取用户数据"""
    # 指定查询集
    queryset = User.objects.all()
    # 指定序列化器
    serializer_class = UserSerializer
    # 使用分页器
    pagination_class = UserPaginator


if __name__ == '__main__':
    pass
