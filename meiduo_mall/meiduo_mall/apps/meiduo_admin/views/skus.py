# -*- coding: UTF-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU, GoodsCategory, SPU
from meiduo_mall.utils.DRF_paginator import MeiduoAdminSKUPaginator
from meiduo_admin.serializers.skus import SKUSerializer, GoodsCategorySerializer, SPUSpecificationsSerializer


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

    def specs(self, request, pk):
        """获取spu商品的规格"""
        # 查询spu商品
        spu = SPU.objects.get(id=pk)
        # 查询spu商品关联的所有规格
        specs = spu.specs.all()
        # 序列化返回
        specs_serial = SPUSpecificationsSerializer(specs, many=True)
        return Response(specs_serial.data)

    def get_queryset(self):
        """重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果，得到查询集"""
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword == '' or keyword is None:
            return SKU.objects.all()
        else:
            return SKU.objects.filter(name__contains=keyword)
