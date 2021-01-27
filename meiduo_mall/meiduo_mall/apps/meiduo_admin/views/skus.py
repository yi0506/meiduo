# -*- coding: UTF-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, GoodsCategory
from meiduo_mall.utils.DRF_paginator import MeiduoAdminSKUPaginator
from meiduo_admin.serializers.skus import SKUSerializer, GoodsCategorySerializer


class SKUView(ModelViewSet):
    """SKU管理"""
    queryset = SKU.objects.all()
    pagination_class = MeiduoAdminSKUPaginator
    serializer_class = SKUSerializer

    @action(methods=['get'], detail=False)  # 自动生成路由
    def categories(self, request):
        """获取商品的三级分类"""
        # .parent: 多查一，查上一级分类
        # .subs: 一查多，查下一级分类
        categories_3 = GoodsCategory.objects.filter(subs__id=None)
        categories_3_serial = GoodsCategorySerializer(categories_3, many=True)
        return Response(categories_3_serial.data)

