# -*- coding: UTF-8 -*-
from rest_framework import serializers

from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {
                "write_only": True,
            },
        }

