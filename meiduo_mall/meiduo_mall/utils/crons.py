# -*- coding: UTF-8 -*-
"""静态化页面"""
from collections import OrderedDict
from django.template import loader
from django.conf import settings
import os

from contents.models import ContentCategory
from meiduo_mall.utils.method_package import get_categories


def generate_static_index_html():
    """首页静态化"""
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
    # 渲染模板
    html_text = loader.render_to_string('index.html', context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'html/index.html')
    # 将模板文件写入静态路径
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)


if __name__ == '__main__':
    pass
