from django.shortcuts import render
from django.views import View
import json
from django import http

from goods.models import SKU


class CartView(View):
    """购物车管理"""
    def post(self, request):
        """保存购物车"""
        # 接收、校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected')  # 可选
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否合法
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        # 判断count是否为整数
        if not isinstance(count, int):
            return http.HttpResponseForbidden('参数count错误')
        # 判断selected是否为bool类型
        if selected is not None:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated is True:
            # 如果用户已登录，操作Redis购物车
            pass
        else:
            # 如果用户未登录，操作cookie购物车
            pass
        # 响应结果