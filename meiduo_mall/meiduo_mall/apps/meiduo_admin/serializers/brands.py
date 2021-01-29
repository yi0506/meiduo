# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import Brand
from meiduo_mall.utils.fastdfs.fdfs_meiduo import FDFS_Client_Meiduo


class BrandSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""

    class Meta:
        model = Brand
        fields = "__all__"

    def create(self, validated_data):
        """保存数据并上传图片"""
        # 验证成功，建立fastdfs客户端
        client_fdfs = FDFS_Client_Meiduo()
        # 获取图片对象
        image = validated_data.get('logo')
        # 上传图片
        res = client_fdfs.upload(image)
        # 判断是否上传成功
        if res == 'Failed!':
            return serializers.ValidationError({'error': '图片上传失败'})
        else:
            # 保存品牌数据到数据库
            brand = Brand.objects.create(logo=res, name=validated_data['name'], first_letter=validated_data['first_letter'])
        # 返回创建的对象
        return brand

    def update(self, instance, validated_data):
        """保存数据并上传图片"""
        # 验证成功，建立fastdfs客户端
        client_fdfs = FDFS_Client_Meiduo()
        # 获取图片对象
        image = validated_data.get('logo')
        # 上传图片
        res = client_fdfs.upload(image)
        # 判断是否上传成功
        if res == 'Failed!':
            return serializers.ValidationError({'error': '图片上传失败'})
        else:
            # 更新品牌数据到数据库
            instance.logo = res
            instance.name = validated_data['name']
            instance.first_letter = validated_data['first_letter']
            instance.save()
        # 返回创建的对象
        return instance
