# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.admins import AdminSerializer
from users.models import User
from meiduo_mall.utils.DRF_paginator import MeiduoAdminAdministratorPaginator


class AdminView(ModelViewSet):
    """权限管理"""
    queryset = User.objects.filter(is_staff=True)
    pagination_class = MeiduoAdminAdministratorPaginator
    serializer_class = AdminSerializer

    # def simple(self, request):
    #     """获取所有权限"""
    #     # 获取所有权限
    #     permissions = Permission.objects.all()
    #     # 序列化返回
    #     permissions_serial = PermissionSerializer(permissions, many=True)
    #     return Response(permissions_serial.data)

