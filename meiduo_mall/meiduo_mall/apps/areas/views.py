from django.shortcuts import render
from django.views import View
from django.db import DatabaseError
from logging import getLogger
from django import http

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE, err_msg


logger = getLogger('django')


class AreaView(View):
    """省市区三级联动"""

    def get(self, request):
        # 判断当前是查询省级数据还是市区级数据
        area_id = request.GET.get('area_id')
        if area_id is None:
            # 省级数据
            try:
                # Area.objects.filter(属性名__条件表达式=值)
                province_model_list = Area.objects.filter(parent__isnull=True)
            except DatabaseError as e:
                logger.error(e)
                return http.JsonResponse({'code': '',
                                          'errmsg': '',
                                          'province_list': '',
                                          })
            pass
        else:
            # 市区级数据
            pass