# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SKU, GoodsCategory


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    class Meta:
        model = SKU
        fields = '__all__'


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = '__all__'
