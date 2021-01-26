# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.images import ImagesSerializer, SKUSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminImagesPaginator


class ImagesView(ModelViewSet):
    """图片管理"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MeiduoAdminImagesPaginator

    def simple(self, request):
        """获取全部商品SKU"""
        # 查询商品sku
        skus = SKU.objects.all()
        # 序列化返回
        skus_serial = SKUSerializer(skus, many=True)
        return Response(skus_serial.data)


if __name__ == '__main__':
    pass
