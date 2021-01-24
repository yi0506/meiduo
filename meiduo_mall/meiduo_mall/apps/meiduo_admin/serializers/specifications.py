# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer

from goods.models import SPUSpecification


class SpecsSerializer(ModelSerializer):
    """商品规格序列化器"""

    class Meta:
        model = SPUSpecification
        fields = '__all__'


if __name__ == '__main__':
    pass
