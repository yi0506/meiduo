# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet

from goods.models import SKU
from meiduo_mall.utils.DRF_paginator import MeiduoAdminSKUPaginator
from meiduo_admin.serializers.skus import SKUSerializer


class SKUView(ModelViewSet):
    """SKU管理"""
    queryset = SKU.objects.all()
    pagination_class = MeiduoAdminSKUPaginator
    serializer_class = SKUSerializer
