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
            redis_conn = get_redis_connection('carts')
            # 查询hash数据，返回dict类型数据：{b'3': b'1'}
            redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
            # 查询set数据，返回set类型数据：{b'3'}
            redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
            # 将redis_cart和redis_selected数据合并，数据结构和未登录用户购物车结构一致
            cart_dict = {}  # 如果查询不到数据，for循环不会执行，cart_dict为空数据
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected,
                }
        else:
            # 用户未登录，查询cookies数据库，判断是否有购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 如果有，提取原来的购物车数据
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                # 如果没有，创建新的购物车数据
                cart_dict = {}
        # 查询购物车中所有的sku
        skus = SKU.objects.filter(id__in=cart_dict.keys())
        cart_skus = []
        # 获取并构造购物车中所有商品的信息
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # 将True，转'True'，方便json解析
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),  # 从Decimal('10.2')中取出'10.2'，方便json解析，通过ORM获取的浮点数是一个Decimal对象
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })
        context = {
            'cart_skus': cart_skus,
        }
        # 响应购物车数据
        return render(request, 'carts.html', context)

    def post(self, request):
        """
        保存购物车

        登录用户购物车数据，保存在Redis中：
                carts_user_id: {sku_id1: count, sku_id3: count, sku_id5: count, ...}
                selected_user_id: [sku_id1, sku_id3, ...]

        未登录用户购物车数据，以字符串保存在cookie中：
                {
                    "sku_id1":{
                        "count":"1",
                        "selected":"True"
                    },
                    "sku_id3":{
                        "count":"3",
                        "selected":"True"
                    },
                    "sku_id5":{
                        "count":"3",
                        "selected":"False"
                    }
                }
        """
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
                    origin_count = cart_dict.get(sku_id).get('count')
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
