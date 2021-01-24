# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SPUSpecification
from meiduo_admin.serializers.specifications import SpecsSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminPaginator


class SpecsView(ModelViewSet):
    """商品规格表增删改查"""
    # 指定查询集
    queryset = SPUSpecification.objects.all()
    # 指定序列化器
    serializer_class = SpecsSerializer
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = MeiduoAdminPaginator


if __name__ == '__main__':
    pass
