# -*- coding: UTF-8 -*-
from collections import OrderedDict

from goods.models import GoodsChannel


def get_breadcrumb(category):
    """
    获取面包屑导航
    :param category: 类别对象：一级、二级、三级类别
    :return 一级类别 ---> 一级，
            二级类别 ---> 一级 + 二级，
            三级类别 ---> 一级 + 二级 + 三级
    """
    breadcrumb = {
        'cat1': '',  # 一级
        'cat2': '',  # 二级
        'cat3': ''  # 三级
    }
    # 判断category是几级类别
    if category.parent is None:  # category为一级类别
        breadcrumb['cat1'] = category
    elif category.subs.count() == 0:  # category为三级类别
        breadcrumb['cat1'] = category.parent.parent
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat3'] = category
    else:  # category为二级类别
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category
    return breadcrumb


def get_categories():
    """获取商品分类三级数据"""
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
    return categories


if __name__ == '__main__':
    pass
