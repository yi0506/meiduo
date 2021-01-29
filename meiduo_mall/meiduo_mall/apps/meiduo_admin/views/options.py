# -*- coding: UTF-8 -*-
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.serializers.options import OptionSerializer, SpecificationsSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminOptionsPaginator


class OptionView(ModelViewSet):
    """规格选项管理"""
    queryset = SpecificationOption.objects.all()
    serializer_class = OptionSerializer
    pagination_class = MeiduoAdminOptionsPaginator

    def simple(self, request):
        """获取所有规格"""
        # 获取所有规格
        specs = SPUSpecification.objects.all()
        # 序列化返回
        specs_serial = SpecificationsSerializer(specs, many=True)
        return Response(specs_serial.data)