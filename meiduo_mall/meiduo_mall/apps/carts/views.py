from django.shortcuts import render
from django.views import View


class CartView(View):
    """购物车管理"""
    def post(self, request):
        """保存购物车"""
        # 接收、校验参数
        # 判断用户是否登录
        # 如果用户已登录，操作Redis购物车
        # 如果用户未登录，操作cookie购物车
        # 响应结果