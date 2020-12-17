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
                    'channels': [],
                    'sub_cats': [],
                }
            # 查询当前频道对应的一级类别
            cat = channel.category
            # 将cat添加到channels，直接通过关联查询（通过group_id一查多，查所有的channel，效率不高）
            categories[group_id]['channels'].append({
                'id': cat.id,
                'name': cat.name,
                'url': channel.url

            })
        return render(request, 'index.html')


class FaviconView(View):
    """favicon图标"""
    def get(self, request):
        """提供favicon图标"""
        return redirect(staticfiles_storage.url('favicon.ico'))
