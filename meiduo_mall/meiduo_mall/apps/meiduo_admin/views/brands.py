# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import Brand
from meiduo_admin.serializers.brands import BrandSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminBrandsPaginator


class ChannelView(ModelViewSet):
    """频道管理"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = MeiduoAdminBrandsPaginator
