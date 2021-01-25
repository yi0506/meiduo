# -*- coding: UTF-8 -*-
from rest_framework import serializers

from goods.models import SKUImage


class ImagesSerializer(serializers.ModelSerializer):
    """SKUImages序列化器"""
    sku_id = serializers.IntegerField()

    class Meta:
        model = SKUImage
        fields = '__all__'


if __name__ == '__main__':
    pass
