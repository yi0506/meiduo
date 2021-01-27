# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    class Meta:
        model = SKU
        fields = '__all__'
        read_only = ('spu', 'category')


class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = '__all__'


class SpecificationsOptionsSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SPUSpecificationsSerializer(serializers.ModelSerializer):
    """SPU商品规格序列化器"""
    # 关联序列化返回 规格选项信息
    options = SpecificationsOptionsSerializer(many=True)
    # 关联序列化返回SPU表数据
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SPUSpecification
        fields = '__all__'
