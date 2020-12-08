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
        """返回省市区三级数据"""
        # 判断当前是查询省级数据还是市区级数据
        # area_id为None则为获取全部省级数据
        # area_id有值，则为省的id 或 市的id
        # area_id为省级id则，通过省级id 找到省，通过这个省 自关联找到下面所有的 市级数据（parent_id为area_id的城市）
        # area_id为市级id则，通过市级id 找到市，通过这个市 自关联找到下面所有的 区级数据（parent_id为area_id的区县）
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
            try:
                # # 直接查询
                # child_model_list = Area.objects.filter(parent_id=area_id)
                # 自关联查询
                parent_model = Area.objects.get(id=area_id)
                sub_model_list = parent_model.subs.all()
            except DatabaseError as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR], 'province_list': []})
            else:
                # 将子集模型列表转成字典列表
                subs = []
                for sub_model in sub_model_list:
                    sub_dict = {
                        'id': sub_model.id,
                        'name': sub_model.name
                    }
                    subs.append(sub_dict)
                sub_data = {
                    'id': parent_model.id,
                    'name': parent_model.name,
                    'subs': subs
                }
                # 响应城市或者区县JSON数据
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'sub_data': sub_data})
