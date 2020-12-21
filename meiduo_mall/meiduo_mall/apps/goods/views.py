from django.shortcuts import render
from django.views import View
from django import http

from goods.models import GoodsCategory, GoodsChannel
from meiduo_mall.utils.method_package import get_categories, get_breadcrumb


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        try:
            # 校验category_id，防止出现 category_id > 商品类别数量
            category = GoodsCategory.objects.get(id=category_id)  # category为三级类别
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id错误')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航： 一级 -> 二级 ->三级
        breadcrumb = get_breadcrumb(category)
        try:
            breadcrumb['cat1'].url = GoodsChannel.objects.get(id=breadcrumb['cat1'].id).url
        except GoodsChannel.DoesNotExist:
            return http.HttpResponseForbidden('一级类别数据错误')
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }
        return render(request, 'list.html', context)

