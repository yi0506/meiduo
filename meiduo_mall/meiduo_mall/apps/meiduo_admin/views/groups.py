# -*- coding: UTF-8 -*-
from django.contrib.auth.models import Group, Permission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.groups import GroupSerializer
from meiduo_admin.serializers.permissions import PermissionSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminGroupPaginator


class GroupView(ModelViewSet):
    """权限管理"""
    queryset = Group.objects.all()
    pagination_class = MeiduoAdminGroupPaginator
    serializer_class = GroupSerializer

    def simple(self, request):
        """获取所有权限"""
        # 获取所有权限
        permissions = Permission.objects.all()
        # 序列化返回
        permissions_serial = PermissionSerializer(permissions, many=True)
        return Response(permissions_serial.data)
