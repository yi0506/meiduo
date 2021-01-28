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

    def get_queryset(self):
        """重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果，得到查询集"""
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)
