from django.shortcuts import render, redirect
from django.views import View
from django.contrib.staticfiles.storage import staticfiles_storage
from collections import OrderedDict

from contents.models import ContentCategory
from meiduo_mall.utils.method_package import get_categories


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""
        # 查询商品分类三级数据
        categories = get_categories()
        # 查询首页广告数据
        contents = OrderedDict()
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            # 使用广告类别查询处该类别对应的所有广告内容
            contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')  # 查询出未下架的广告并排序
        # 构造上下文
        context = {
            'categories': categories,
            'contents': contents
        }
        return render(request, 'index.html', context)


class FaviconView(View):
    """favicon图标"""
    def get(self, request):
        """提供favicon图标"""
        return redirect(staticfiles_storage.url('favicon.ico'))
