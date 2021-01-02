# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 结算订单页面
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
    # 提交订单
    url(r'^orders/commit/$', views.OrderCommitView.as_view()),
    # 提交订单成功页面
    url(r'^orders/success/$', views.OrderSuccessView.as_view()),
    # 展示个人订单中心
    url(r'^orders/info/(?P<page_num>\d+)/$', views.UserOrderInfoView.as_view(), name='info'),
    # 展示商品评价页面
    url(r'^orders/comment/$', views.OrderCommentView.as_view()),
    # 商品详情页展示评价信息
    url(r'^comments/(?P<sku_id>\d+)/$', views.GoodsCommentView.as_view()),
]


if __name__ == '__main__':
    pass
