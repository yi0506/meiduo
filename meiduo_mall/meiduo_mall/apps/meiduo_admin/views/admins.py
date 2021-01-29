# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group

from meiduo_admin.serializers.admins import AdminSerializer
from meiduo_admin.serializers.groups import GroupSerializer
from users.models import User
from meiduo_mall.utils.DRF_paginator import MeiduoAdminAdministratorPaginator


class AdminView(ModelViewSet):
    """权限管理"""
    queryset = User.objects.filter(is_staff=True)
    pagination_class = MeiduoAdminAdministratorPaginator
    serializer_class = AdminSerializer

    def simple(self, request):
        """获取所有权限"""
        # 获取所有权限
        data = Group.objects.all()
        # 序列化返回
        ser = GroupSerializer(data, many=True)
        return Response(ser.data)

