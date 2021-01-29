# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SPUSpecification, SpecificationOption


class OptionSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = "__all__"


class SpecificationsSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = "__all__"
