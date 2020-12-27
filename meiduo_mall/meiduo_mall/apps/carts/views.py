from django.shortcuts import render
from django.views import View
import json
from django import http
from django_redis import get_redis_connection
from logging import getLogger

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE, err_msg


logger = getLogger('django')


class CartView(View):
    """购物车管理"""
    def post(self, request):
        """保存购物车"""
        # 接收、校验参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)  # 可选，默认购物车中商品都会被勾选
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否合法
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        # 判断count是否为整数
        if not isinstance(count, int):
            return http.HttpResponseForbidden('参数count错误')
        # 判断selected是否为bool类型
        if selected is not True:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated():
            # 如果用户已登录，操作Redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 需要以增量计算的形式保存商品数据
            pl.hincrby('carts_{}'.format(user.id), sku_id, count)
            # 保存商品勾选状态
            if selected is True:
                pl.sadd('selected_{}'.format(user.id), sku_id)
            try:
                # 执行管道
                pl.execute()
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})
        else:
            # 如果用户未登录，操作cookie购物车
            pass
        # 响应结果