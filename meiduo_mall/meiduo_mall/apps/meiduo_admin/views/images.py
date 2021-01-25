# -*- coding: UTF-8 -*-
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage
from meiduo_admin.serializers.images import ImagesSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminImagesPaginator


class ImagesView(ModelViewSet):
    """图片管理"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MeiduoAdminImagesPaginator


if __name__ == '__main__':
    pass
