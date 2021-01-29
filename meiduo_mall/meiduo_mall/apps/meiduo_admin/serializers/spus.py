# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SPU, Brand, GoodsCategory


class BrandSerializer(serializers.ModelSerializer):
    """Brand序列化器"""
    class Meta:
        model = Brand
        fields = "__all__"


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = GoodsCategory
        fields = "__all__"


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()
    brand = serializers.PrimaryKeyRelatedField(read_only=True)
    category1 = serializers.PrimaryKeyRelatedField(read_only=True)
    category2 = serializers.PrimaryKeyRelatedField(read_only=True)
    category3 = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SPU
        fields = "__all__"

    # def create(self, validated_data):
    #     pass

