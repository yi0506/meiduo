# -*- coding: UTF-8 -*-
from django.conf.urls import url, include

from . import views


urlpatterns = [
    # 商品列表页
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.ListView.as_view(), name='list'),

]

if __name__ == '__main__':
    pass
