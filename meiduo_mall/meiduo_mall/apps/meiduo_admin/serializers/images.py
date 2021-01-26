# -*- coding: UTF-8 -*-
from rest_framework import serializers
from goods.models import SKUImage, SKU

from meiduo_mall.utils.fastdfs.fdfs_meiduo import FDFS_Client_Meiduo
from celery_tasks.static_file.tasks import generate_static_sku_detail_html


class ImagesSerializer(serializers.ModelSerializer):
    """SKUImages序列化器"""

    class Meta:
        model = SKUImage
        fields = '__all__'

    def create(self, validated_data):
        """上传图片"""
        # 验证成功，建立fastdfs客户端
        client_fdfs = FDFS_Client_Meiduo()
        # 获取图片对象
        image = validated_data.get('image')
        # 上传图片
        res = client_fdfs.upload(image)
        # 判断是否上传成功
        if res == 'Failed!':
            return serializers.ValidationError({'error': '图片上传失败'})
        # 保存图片数据到数据库
        sku_img = SKUImage.objects.create(sku=validated_data['sku'], image=res)
        # 异步执行页面静态化
        generate_static_sku_detail_html.delay(sku_img.sku.id)
        # 返回创建的对象
        return sku_img

    def update(self, instance, validated_data):
        """更新图片"""
        # 验证成功，建立fastdfs客户端
        client_fdfs = FDFS_Client_Meiduo()
        # 获取图片对象
        image = validated_data.get('image')
        # 上传图片
        res = client_fdfs.upload(image)
        # 判断是否上传成功
        if res == 'Failed!':
            return serializers.ValidationError({'error': '图片上传失败'})
        # 更新图片数据到数据库
        instance.image = res
        instance.save()
        # 异步执行页面静态化
        generate_static_sku_detail_html.delay(instance.sku.id)
        # 返回创建的对象
        return instance


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""

    class Meta:
        model = SKU
        fields = ('id', 'name')


if __name__ == '__main__':
    pass
