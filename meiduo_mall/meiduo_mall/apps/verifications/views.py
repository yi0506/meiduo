from django.shortcuts import render
from django.views import View
# Create your views here.


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别码，用于唯一标识该图形验证属于哪个用户的
        :return: image/jpg
        """
        pass
