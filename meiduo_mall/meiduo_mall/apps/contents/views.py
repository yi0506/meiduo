from django.shortcuts import render, redirect
from django.views import View
from django.contrib.staticfiles.storage import staticfiles_storage
from collections import OrderedDict

from goods.models import GoodsCategory, GoodsChannel, GoodsChannelGroup


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""
        # 准备商品分类字典，有序字典
        categories = OrderedDict()
        # 查询所有的商品频道：37个一级类别，对查询结果进行排序
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        # 遍历所有频道
        for channel in channels:
            # 获取当前频道所在的组,group_id为频道组编号
            group_id = channel.group_id
            # 只有11个频道组
            if group_id not in categories:
                categories[group_id] = {
                    'channels': [],  # 所有的频道 channel，一级类别
                    'sub_cats': [],  # 二级、三级类别
                }
            # 查询当前频道对应的一级类别，通过channel，承上启下，向上查GoodsChannelGroup，向下查GoodsCategory
            cat_1 = channel.category
            # 将cat添加到channels，直接通过关联查询（通过group_id一查多，查所有的channel，效率不高）
            categories[group_id]['channels'].append({
                'id': cat_1.id,
                'name': cat_1.name,
                'url': channel.url
            })
            # 查询二级和三级类别
            for cat_2 in cat_1.subs.all():  # 该一级类别下所有的二级类别
                cat_2.sub_cats = []  # # 动态添加一个sub_cats属性，存放该二级类别下的所有三级类别，GoodsCategory模型类本身没有该sub_cats属性，因此数据库中也没有该字段
                for cat_3 in cat_2.subs.all():  # 该二级类别下所有的三级类别
                    cat_2.sub_cats.append(cat_3)
                # 将二级类别添加到一级类别的sub_cats中
                categories[group_id]['sub_cats'].append(cat_2)
        # 构造上下文
        context = {
            'categories': categories
        }
        return render(request, 'index.html', context)


class FaviconView(View):
    """favicon图标"""
    def get(self, request):
        """提供favicon图标"""
        return redirect(staticfiles_storage.url('favicon.ico'))
