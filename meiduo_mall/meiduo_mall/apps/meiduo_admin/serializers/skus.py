# -*- coding: UTF-8 -*-
from rest_framework import serializers
from django.db import transaction
from logging import getLogger

from goods.models import SKU, GoodsCategory, SPUSpecification, SpecificationOption, SKUSpecification
from celery_tasks.static_file.tasks import generate_static_sku_detail_html


logger = getLogger('django')


class SKUSpecificationSerializer(serializers.ModelSerializer):
    """SKU规格表序列化器"""

    spec_id = serializers.IntegerField(read_only=True)
    option_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SKUSpecification  # SKUSpecification中sku外键关联了SKU表
        fields = ("spec_id", 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    # 指定所关联的SKU规格选项信息 关联嵌套返回
    specs = SKUSpecificationSerializer(read_only=True, many=True)
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    class Meta:
        model = SKU
        fields = '__all__'
        read_only_fields = ('spu', 'category')

    def create(self, validated_data):
        """使用事务保存sku表信息与sku_specifications表信息"""
        # sku的所有规格信息
        sku_specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                # 保存sku表
                sku = SKU.objects.create(default_image='group1/M00/00/02/CtM3BVrRdQSAHxqbAAQ3kdJbqeQ1136308', **validated_data)
                # 保存sku_specifications表
                for sku_spec in sku_specs:
                    SKUSpecification.objects.create(spec_id=sku_spec['spec_id'], option_id=sku_spec['option_id'], sku=sku)
            except Exception as e:
                # 回滚
                transaction.savepoint_rollback(save_point)
                logger.error(e)
                raise serializers.ValidationError('sku保存失败')
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)
                # 生成详情页静态页面
                generate_static_sku_detail_html.delay(sku.id)
                return sku

    def update(self, sku, validated_data):
        """完成sku表的更新"""
        # sku的所有规格信息
        sku_specs = self.context['request'].data.get('specs')
        # 开启事务
        with transaction.atomic():
            # 设置保存点
            save_point = transaction.savepoint()
            try:
                # 保存sku表
                SKU.objects.filter(id=sku.id).update(**validated_data)
                # 保存sku_specifications表
                for sku_spec in sku_specs:
                    SKUSpecification.objects.filter(sku=sku).update(**sku_spec)
            except Exception as e:
                # 回滚
                transaction.savepoint_rollback(save_point)
                logger.error(e)
                raise serializers.ValidationError('sku保存失败')
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)
                # 生成详情页静态页面
                generate_static_sku_detail_html.delay(sku.id)
                return sku


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
