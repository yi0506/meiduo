# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup
from meiduo_admin.serializers.channels import ChannelSerializer, GoodsCategorySerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminChannelsPaginator


class ChannelView(ModelViewSet):
    """频道管理"""
    queryset = GoodsChannel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = MeiduoAdminChannelsPaginator

    def category(self, request):
        """获取频道一级分类"""
        categorys = GoodsCategory.objects.filter(parent=None)
        ser = GoodsCategorySerializer(categorys, many=True)
        return Response(ser.data)

    def channel_types(self, request):
        """获取频道一级分类"""
        groups = GoodsChannelGroup.objects.all()
        ser = GoodsCategorySerializer(groups, many=True)
        return Response(ser.data)