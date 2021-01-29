# -*- coding: UTF-8 -*-
from django.contrib.auth.models import Permission
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.permissions import PermissionSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminPermissionPaginator


class PermissionView(ModelViewSet):
    """权限管理"""
    queryset = Permission.objects.all()
    pagination_class = MeiduoAdminPermissionPaginator
    serializer_class = PermissionSerializer
