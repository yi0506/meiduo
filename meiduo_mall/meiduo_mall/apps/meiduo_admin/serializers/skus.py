# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    class Meta:
        model = SKU
        fields = '__all__'
