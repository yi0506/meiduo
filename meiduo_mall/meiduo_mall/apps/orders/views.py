from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from logging import getLogger
from django_redis import get_redis_connection
from decimal import Decimal

from users.models import Address
from goods.models import SKU
from meiduo_mall.utils import constants


logger = getLogger('django')


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
