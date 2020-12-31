from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone

from users.models import Address
from goods.models import SKU
from meiduo_mall.utils import constants
from meiduo_mall.utils.auth_backend import LoginRequiredJsonMixin
from .models import OrderInfo
from meiduo_mall.utils.response_code import RETCODE, err_msg


logger = getLogger('django')


class OrderCommitView(LoginRequiredJsonMixin, View):
    """提交订单"""
    def post(self, request):
        """保存订单基本信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')
        # 获取登录用户
        user = request.user
        # 获取订单编号：时间 + user_id == '2020123113041200000001'
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '{:0>9d}'.format(user.id)
        # 保存订单基本信息(一)
        OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            address=address,
            total_count=0,  # 仅用来初始化，后面根据订单中的商品进行更新
            total_amount=Decimal('0.00'),  # 仅用来初始化，后面根据订单中的商品进行更新
            freight=Decimal(constants.ORDERS_FREIGHT_COST),
            pay_method=pay_method,
            # 如果支付方式为支付宝，支付状态为未付款，如果支付方式是货到付款，支付状态为未发货
            status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        )
        # 保存订单商品信息(多)
        pass
        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'order_id': order_id})


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """查询并展示要结算的订单数据"""
        # 获取登录用户
        user = request.user
        # 查询用户收货地址，没有被删除的收货地址
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            logger.error(e)
            # 如果没有查询出收货地址，可以去编辑收货地址
            addresses = None
        # 查询redis中购物车被勾选的商品
        redis_conn = get_redis_connection('carts')
        # 购物车中商品的数量
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        # 被勾选的商品sku_id
        redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
        # 构造购物车中被勾选商品的数据 new_cart_dict
        new_cart_dict = {}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
        # 获取被勾选商品的sku_id
        sku_ids = new_cart_dict.keys()
        # 获取被勾选商品的sku信息
        skus = SKU.objects.filter(id__in=sku_ids)
        # 商品总数量与商品总金额
        total_count = 0
        total_amount = Decimal(0.00)  # 或 Decimal('0.00')
        for sku in skus:
            # 遍历skus，给每个sku补充count（数量）和amount（小计）字段
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count  # Decimal类型
            # 累加商品数量和金额
            total_count += sku.count
            total_amount += sku.amount
        # 构造上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': constants.ORDERS_FREIGHT_COST,  # 运费
            'payment_amount': Decimal(constants.ORDERS_FREIGHT_COST) + total_amount,
        }
        return render(request, 'place_order.html', context)
