# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from goods.models import SPUSpecification, SPU


class SpecsSerializer(ModelSerializer):
    """商品规格序列化器"""
    # 指定关联模型的数据返回形式
    spu = serializers.StringRelatedField(read_only=True)  # 根据关联模型的方式取数据
    spu_id = serializers.IntegerField()  # 根据数据表中的外键字段取数据

    class Meta:
        model = SPUSpecification
        fields = '__all__'


class SPUSerializer(ModelSerializer):
    """SPU序列化器"""

    class Meta:
        model = SPU
        fields = ('id', 'name')


if __name__ == '__main__':
    pass
