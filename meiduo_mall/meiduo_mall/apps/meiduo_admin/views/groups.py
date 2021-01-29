# -*- coding: UTF-8 -*-
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.groups import GroupSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminGroupPaginator


class GroupView(ModelViewSet):
    """权限管理"""
    queryset = Group.objects.all()
    pagination_class = MeiduoAdminGroupPaginator
    serializer_class = GroupSerializer
