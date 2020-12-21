from django.shortcuts import render
from django.views import View
from django import http

from goods.models import GoodsCategory
from meiduo_mall.utils.method_package import get_categories


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id错误')
        # 查询商品分类
        categories = get_categories()
        # 构造上下文
        context = {
            'categories': categories,
        }
        return render(request, 'list.html', context)

