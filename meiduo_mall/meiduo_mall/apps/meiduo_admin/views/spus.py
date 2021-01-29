# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, Brand, GoodsCategory
from meiduo_admin.serializers.spus import SPUSerializer, GoodsCategorySerializer, BrandSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminSPUPaginator


class SPUView(ModelViewSet):
    """SPU管理"""
    queryset = SPU.objects.all()
    serializer_class = SPUSerializer
    pagination_class = MeiduoAdminSPUPaginator

    def simple(self, request):
        """获取商品品牌"""
        # 获取spu数据
        spus = Brand.objects.all()
        # 序列化返回
        spus_serial = BrandSerializer(spus, many=True)
        return Response(spus_serial.data)

    def category_23(self, request, pk):
        """获取二三级分类"""
        # 获取全部一级
        spus = GoodsCategory.objects.get(id=pk).subs.all()
        # 序列化返回
        spus_serial = GoodsCategorySerializer(spus, many=True)
        return Response(spus_serial.data)

    def category_1(self, request, pk=None):
        """获取一级分类"""
        # 获取二三级
        spus = GoodsCategory.objects.all()
        # 序列化返回
        spus_serial = GoodsCategorySerializer(spus, many=True)
        return Response(spus_serial.data)

