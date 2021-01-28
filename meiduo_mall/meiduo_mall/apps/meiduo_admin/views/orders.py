# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from logging import getLogger

from meiduo_admin.serializers.orders import OrderSerializer
from orders.models import OrderInfo
from meiduo_mall.utils.DRF_paginator import MeiduoAdminOrdersPaginator


logger = getLogger('django')


class OrdersView(ReadOnlyModelViewSet):
    """订单信息管理"""
    queryset = OrderInfo.objects.all()
    serializer_class = OrderSerializer
    pagination_class = MeiduoAdminOrdersPaginator
    lookup_field = 'order_id'

    def get_queryset(self):
        """重写get_queryset方法，根据前端是否传递keyword值返回不同查询结果，得到查询集"""
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword == '' or keyword is None:
            return OrderInfo.objects.all()
        else:
            return OrderInfo.objects.filter(order_id__contains=keyword)

    @action(methods=['patch'], detail=True)
    def status(self, request, order_id):
        """修改订单状态"""
        # 查询要修改的订单对象
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist as e:
            logger.error(e)
            return Response({'error', '订单编号错误'})
        # 获取订单状态
        status = request.data.get('status')
        # 修改订单状态
        order.status = status
        order.save()
        # 返回修改信息
        return Response({'status': status, 'order_id': order_id})
