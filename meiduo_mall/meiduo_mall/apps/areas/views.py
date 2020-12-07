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
                # 将模型列表转换为字典列表
                province_list = []
                for province_model in province_model_list:
                    province_dict = {
                        'id': province_model.id,
                        'name': province_model.name,
                    }
                    province_list.append(province_dict)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'province_list': province_list})
            except DatabaseError as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR], 'province_list': []})
        else:
            # 市区级数据
            pass