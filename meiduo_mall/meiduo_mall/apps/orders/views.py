from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from django_redis import get_redis_connection
from decimal import Decimal
import json
from django import http
from django.utils import timezone
from django.db import transaction

from users.models import Address
from goods.models import SKU
from meiduo_mall.utils import constants
from meiduo_mall.utils.auth_backend import LoginRequiredJsonMixin
from .models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE, err_msg


logger = getLogger('django')


class OrderSuccessView(LoginRequiredMixin, View):
    """订单成功页面"""
    def get(self, request):
        """提供订单成功页面"""
        # 接受参数
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')
        # 构造上下文
        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method
        }
        return render(request, 'order_success.html', context)


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
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('参数address_id错误')
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method错误')
        # 获取登录用户
        user = request.user
        # 获取订单编号：时间 + user_id == '2020123113041200000001'
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '{:0>9d}'.format(user.id)
        # 以下操作数据库的操作，开启作为一次事务
        with transaction.atomic():
            # 在数据库操作前，创建保存点（数据库最初的状态）
            save_id = transaction.savepoint()
            # 对于未知错误，暴力回滚
            try:
                # 保存订单基本信息(一)
                order = OrderInfo.objects.create(
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
                # 查询redis中购物车被勾选的商品
                redis_conn = get_redis_connection('carts')
                # 购物车中商品的数量
                redis_cart = redis_conn.hgetall('carts_%s' % user.id)
                # 被勾选的商品sku_id
                redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
                # 构造购物车中被勾选商品的数据 new_cart_dict，{sku_id: 2, sku_id: 1}
                new_cart_dict = {}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])
                # 获取被勾选商品的sku_id
                sku_ids = new_cart_dict.keys()
                for sku_id in sku_ids:
                    # 读取商品的sku信息
                    sku = SKU.objects.get(id=sku_id)  # 查询商品和库存信息时，不能出现缓存，所有不用 filter(id__in=sku_ids)
                    # 获取当前被勾选商品的库存
                    sku_count = new_cart_dict[sku.id]
                    # 如果订单中的商品数量大于库存，响应库存不足
                    if sku_count > sku.stock:
                        # 库存不足，回滚
                        transaction.savepoint_rollback(save_id)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': err_msg[RETCODE.STOCKERR]})
                    # 如果库存满足，SKU 减库存，加销量
                    sku.stock -= sku_count
                    sku.sales += sku_count
                    sku.save()
                    # SPU 加销量
                    sku.spu.sales += sku_count
                    sku.spu.save()
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price,
                    )
                    # 累加订单中商品的总价和总数量
                    order.total_count += sku_count
                    order.total_amount += (sku_count * sku.price)
                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.ORDEROPERATEERR, 'errmsg': err_msg[RETCODE.ORDEROPERATEERR]})
            else:
                # 提交事务
                transaction.savepoint_commit(save_id)
        # 清除购物车中已结算的商品
        pl = redis_conn.pipeline()
        pl.hdel('carts_%s' % user.id, *redis_selected)
        pl.srem('selected_%s' % user.id, *redis_selected)
        try:
            pl.execute()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DUPLICATEORDERERR, 'errmsg': err_msg[RETCODE.DUPLICATEORDERERR]})
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
        # 构造购物车中被勾选商品的数据 new_cart_dict，{sku_id: 2, sku_id: 1}
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
