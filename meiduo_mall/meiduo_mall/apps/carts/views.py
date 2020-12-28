from django.shortcuts import render
from django.views import View
import json
from django import http
from django_redis import get_redis_connection
from logging import getLogger
import base64
import pickle

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE, err_msg
from meiduo_mall.utils import constants


logger = getLogger('django')


class CartsView(View):
    """购物车管理"""
    def get(self, request):
        """查询购物车"""
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis数据库
            pass
        else:
            # 用户未登录，查询cookies数据库
            pass
        return render(request, 'carts.html')

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
        if user.is_authenticated:
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
            # 获取cookies中的购物车数据，判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 如果有，提取原来的购物车数据
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
                # 判断当前要添加的商品是否在购物车cart_dict中
                if sku_id in cart_dict:
                    # 如果有，更新当前商品的数量，做增量计算
                    origin_count = cart_dict[sku_id]['count']
                    count += origin_count
            else:
                # 如果没有，创建新的购物车数据
                cart_dict = {}
            # 更新购物车数据
            cart_dict[sku_id] = {'count': count, 'selected': selected}
            # 购物车数据加密序列化
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_bytes_str = base64.b64encode(cart_dict_bytes)
            cart_str = cart_bytes_str.decode()
            # 将新的购物车数据写入到cookies中
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})
            response.set_cookie('carts', cart_str, max_age=constants.ANONYMOUS_USER_CART_EXPIRES)
        # 响应结果
        return response
