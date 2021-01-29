# -*- coding: UTF-8 -*-
from django.contrib.auth.models import Permission, ContentType
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.permissions import PermissionSerializer, ContentTypeSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminPermissionPaginator


class PermissionView(ModelViewSet):
    """权限管理"""
    queryset = Permission.objects.all()
    pagination_class = MeiduoAdminPermissionPaginator
    serializer_class = PermissionSerializer

    def content_type(self, request):
        """获取权限类型"""
        # 获取所有权限
        content_types = ContentType.objects.all()
        # 序列化返回
        types_serial = ContentTypeSerializer(content_types, many=True)
        return Response(types_serial.data)
