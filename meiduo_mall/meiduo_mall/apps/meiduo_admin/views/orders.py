# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ReadOnlyModelViewSet

from meiduo_admin.serializers.orders import OrderSerializer
from orders.models import OrderInfo
from meiduo_mall.utils.DRF_paginator import MeiduoAdminOrdersPaginator


class OrdersView(ReadOnlyModelViewSet):
    """订单信息管理"""
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer
    pagination_class = MeiduoAdminOrdersPaginator
