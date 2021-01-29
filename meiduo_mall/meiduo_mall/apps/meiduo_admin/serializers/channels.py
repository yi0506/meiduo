# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import GoodsChannel, GoodsCategory


class ChannelSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""
    group_id = serializers.IntegerField()
    group = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    category = serializers.StringRelatedField()

    class Meta:
        model = GoodsChannel
        fields = "__all__"


class GoodsCategorySerializer(serializers.ModelSerializer):
    """规格选项序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ('name', 'id')
