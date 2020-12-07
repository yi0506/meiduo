# -*- coding: UTF-8 -*-
from django.conf.urls import url

from . import views


urlpatterns = [
    # 省市区三级联动
    url(r'^areas/', views.AreaView.as_view()),
]


if __name__ == '__main__':
    pass
