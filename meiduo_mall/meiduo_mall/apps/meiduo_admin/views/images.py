# -*- coding: UTF-8 -*-
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SKUImage, SKU
from meiduo_admin.serializers.images import ImagesSerializer, SKUSerializer
from meiduo_mall.utils.DRF_paginator import MeiduoAdminImagesPaginator


class ImagesView(ModelViewSet):
    """图片管理"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MeiduoAdminImagesPaginator

    def simple(self, request):
        """获取全部商品SKU"""
        # 查询商品sku
        skus = SKU.objects.all()
        # 序列化返回
        skus_serial = SKUSerializer(skus, many=True)
        return Response(skus_serial.data)

    # def create(self, request, *args, **kwargs):
    #     """保存图片数据"""
    #     # 获取前端数据
    #     data = request.data
    #     # 反序列化，验证数据
    #     serial = self.get_serializer(data=data)
    #     serial.is_valid(raise_exception=True)
    #     # 如果验证成功，建立fastdfs客户端
    #     client_fdfs = Fdfs_client(settings.FDFS_CONF_PATH)
    #     # 上传图片
    #     image = serial.validated_data.get('image')
    #     res = client_fdfs.upload_by_buffer(image.read())
    #     # 判断是否上传成功
    #     if res['Status'] != 'Upload successed.':
    #         return Response({'error': '图片上传失败'})
    #     # 保存图片数据到数据库
    #     sku_img = SKUImage.objects.create(sku=serial.validated_data['sku'], image=res['Remote file_id'].replace('\\', '/'))
    #     # 序列化返回
    #     sku_img_serial = self.get_serializer(sku_img)
    #     return Response(sku_img_serial.data, status=201)


if __name__ == '__main__':
    pass
