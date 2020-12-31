# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 结算订单页面
    url(r'^orders/settlement/$', views.OrderSettlementView.as_view(), name='settlement'),
]


if __name__ == '__main__':
    pass
