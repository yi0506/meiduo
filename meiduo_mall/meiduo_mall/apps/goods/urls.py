# -*- coding: UTF-8 -*-
from django.conf.urls import url, include

from . import views


urlpatterns = [
    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),
    # 热销排行
    url(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
    # 商品详情
    url(r'^detail/(?P<sku_id>\d+).html$', views.DetailView.as_view(), name='detail'),
    # 统计分类商品的访问量
    url(r'^detail/visit/(?P<category_id>\d+)/$', views.DetailVisitView.as_view())

]

if __name__ == '__main__':
    pass
