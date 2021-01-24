# -*- coding: UTF-8 -*-
from rest_framework.generics import ListAPIView

from meiduo_admin.serializers.users import UserSerializer
from meiduo_mall.utils.DRF_paginator import UserPaginator
from users.models import User


class UserView(ListAPIView):
    """获取用户数据"""
    # 指定序列化器
    serializer_class = UserSerializer
    # 使用分页器
    pagination_class = UserPaginator

    def get_queryset(self):
        """重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果，得到查询集"""
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword is '':
            return User.objects.all()
        else:
            return User.objects.filter(username__contains=keyword)


if __name__ == '__main__':
    pass
