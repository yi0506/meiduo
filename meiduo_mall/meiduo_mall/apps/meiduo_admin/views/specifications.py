# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SPUSpecification, SPU
from meiduo_admin.serializers.specifications import SpecsSerializer, SPUSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminPaginator, MeiduoAdminSPUPaginator


class SpecsView(ModelViewSet):
    """商品规格表增删改查"""
    # 指定查询集
    queryset = SPUSpecification.objects.all()
    # 指定序列化器
    serializer_class = SpecsSerializer
    # 指定权限
    permission_classes = [IsAdminUser]
    # 指定分页器
    pagination_class = MeiduoAdminSPUPaginator

    def simple(self, request):
        """获取SPU商品"""
        spus = SPU.objects.all()
        spus_serial = SPUSerializer(spus, many=True)
        return Response(spus_serial.data)


if __name__ == '__main__':
    pass
