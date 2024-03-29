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


class CartsSimpleView(View):
    """商品页面右上角购物车"""
    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            cart_selected = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的两个数据统一格式，跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in cart_selected
                }
        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
        # 构造简单购物车JSON数据
        cart_skus = []
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict.get(sku.id).get('count'),
                'default_image_url': sku.default_image.url
            })
        # 响应json列表数据
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'cart_skus': cart_skus})


class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        """实现全选购物车逻辑"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        # 校验参数
        if selected is not True:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected有误')
        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录，全选redis购物车
            redis_conn = get_redis_connection('carts')
            # redis_cart: sku_id: count --> {b'3': b'1', b'5': b'2'}
            redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
            # 判断用户是否全选
            if selected:
                # 全选
                redis_conn.sadd('selected_{}'.format(user.id), *redis_cart.keys())
            else:
                # 取消全选
                redis_conn.srem('selected_{}'.format(user.id), *redis_cart.keys())
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})
        else:
            # 用户未登录，全选cookie购物车
            cart = request.COOKIES.get('carts')
            # 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '全选购物车成功'})
            if cart:
                # 购物车中有数据，才有全选按钮，因此不需要else
                cart = pickle.loads(base64.b64decode(cart.encode()))
                for sku_id in cart:
                    # 完成全选和取消全选
                    cart[sku_id]['selected'] = selected  # True / False
                cookie_cart = base64.b64encode(pickle.dumps(cart)).decode()
                response.set_cookie('carts', cookie_cart, max_age=constants.ANONYMOUS_USER_CART_EXPIRES)
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class CartsView(View):
    """购物车管理"""
    def delete(self, request):
        """删除购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品不存在')
        # 判断用户是否登录
        user = request.user
        if user is not None and user.is_authenticated:
            # 用户已登录，删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_{}'.format(user.id), sku_id)
            pl.srem('selected_{}'.format(user.id), sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})
        else:
            # 用户未登录，删除cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 判断是否存在购物车数据
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 创建响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})
            if sku_id in cart_dict:
                # 如果存在该商品，删除sku_id对应的商品
                del cart_dict[sku_id]
                # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
                cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 响应结果并将购物车数据写入到cookie
                response.set_cookie('carts', cookie_cart_str, max_age=constants.ANONYMOUS_USER_CART_EXPIRES)
            return response

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('商品sku_id不存在')
        # 判断count是否为整数
        if not isinstance(count, int):
            return http.HttpResponseForbidden('参数count错误')
        # 判断selected是否为bool类型
        if selected is not True:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')
        # 创建数据对象
        cart_sku = {
            'id': sku_id,
            'count': count,
            'selected': selected,
            'name': sku.name,
            'default_image_url': sku.default_image.url,
            'price': sku.price,
            'amount': sku.price * count,
        }
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 由于后端收到的商品数量是最终结果，因此直接覆盖写入
            pl.hset('carts_%s' % user.id, sku_id, count)
            # 修改勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'cart_sku': cart_sku})
        else:
            # 用户未登录，修改cookies中的购物车数据
            cart_str = request.COOKIES.get('carts')
            # 判断是否有购物车数据
            if cart_str:
                # 如果有，提取原来的购物车数据
                cart_str_bytes = cart_str.encode()
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                # 如果没有，创建新的购物车数据
                cart_dict = {}
            # 修改购物车数据，后端收到的是最终的商品数量，覆盖写入
            cart_dict[sku_id] = {'count': count, 'selected': selected}
            # 购物车数据加密序列化
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_bytes_str = base64.b64encode(cart_dict_bytes)
            cart_str = cart_bytes_str.decode()
            # 响应结果
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'cart_sku': cart_sku})
            response.set_cookie('carts', cart_str, max_age=constants.ANONYMOUS_USER_CART_EXPIRES)
            return response

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
