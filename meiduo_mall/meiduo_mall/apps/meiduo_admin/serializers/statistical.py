# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer, StringRelatedField

from goods.models import GoodsVisitCount


class GoodsDayVisitSerializer(ModelSerializer):
    """GoodsVisitCount模型类序列化器"""
    category = StringRelatedField(read_only=True)

    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')


if __name__ == '__main__':
    pass
