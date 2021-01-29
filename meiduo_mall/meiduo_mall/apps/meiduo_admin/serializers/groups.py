# -*- coding: UTF-8 -*-
from rest_framework import serializers
from django.contrib.auth.models import Group


class GroupSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = Group
        fields = "__all__"
