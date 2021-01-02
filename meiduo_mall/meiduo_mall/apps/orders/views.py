from django.core.paginator import Paginator, EmptyPage
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


class GoodsCommentView(View):
    """订单商品评价信息"""
    def get(self, request, sku_id):
        # 获取被评价的订单商品信息
        order_goods_list = OrderGoods.objects.filter(sku_id=sku_id, is_commented=True).order_by('-create_time')[:constants.COMMENTS_LIST_LIMIT]
        # 序列化
        comment_list = []
        for order_goods in order_goods_list:
            username = order_goods.order.user.username
            comment_list.append({
                'username': username[0] + '***' + username[-1] if order_goods.is_anonymous else username,
                'comment': order_goods.comment,
                'score': order_goods.score,
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'comment_list': comment_list})


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""
    def get(self, request):
        """展示商品评价页面"""
        # 接收参数
        order_id = request.GET.get('order_id')
        # 校验参数
        try:
            OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseNotFound('订单不存在')
        # 查询订单中未被评价的商品信息
        try:
            uncomment_goods = OrderGoods.objects.filter(order_id=order_id, is_commented=False)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('订单商品信息出错')
        # 构造待评价商品数据
        uncomment_goods_list = []
        for goods in uncomment_goods:
            uncomment_goods_list.append({
                'order_id': goods.order.order_id,
                'sku_id': goods.sku.id,
                'name': goods.sku.name,
                'price': str(goods.price),
                'default_image_url': goods.sku.default_image.url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            })
        # 渲染模板
        context = {
            'uncomment_goods_list': uncomment_goods_list
        }
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """评价订单商品"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 校验参数
        if not all([order_id, sku_id, score, comment]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            OrderInfo.objects.filter(order_id=order_id, user=request.user, status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('参数order_id错误')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数sku_id错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('参数is_anonymous错误')
        # 以下操作数据库的操作，开启作为一次事务
        with transaction.atomic():
            # 在数据库操作前，创建保存点（数据库最初的状态）
            save_id = transaction.savepoint()
            try:
                # 保存订单商品评价数据
                OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id, is_commented=False).update(
                    comment=comment,
                    score=score,
                    is_anonymous=is_anonymous,
                    is_commented=True
                )
                # 累计评论数据
                sku.comments += 1
                sku.save()
                sku.spu.comments += 1
                sku.spu.save()
                # 如果所有订单商品都已评价，则修改订单状态为已完成
                if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
                    OrderInfo.objects.filter(order_id=order_id).update(status=OrderInfo.ORDER_STATUS_ENUM['FINISHED'])
            # 对于未知的数据库错误，暴力回滚
            except Exception as e:
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.COMMITMENTERR, 'errmsg': err_msg[RETCODE.COMMITMENTERR]})
            else:
                # 提交事务
                transaction.savepoint_commit(save_id)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request, page_num):
        """提供我的订单页面"""
        user = request.user
        # 查询订单
        orders = user.orderinfo_set.all().order_by("-create_time")
        # 遍历所有订单
        for order in orders:
            # 绑定订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status-1][1]
            # 绑定支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method-1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)
        # 分页
        page_num = int(page_num)
        try:
            paginator = Paginator(orders, constants.ORDERS_LIST_LIMIT)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except EmptyPage:
            return http.HttpResponseNotFound('订单不存在')
        context = {
            "page_orders": page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, "user_center_order.html", context)


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
        # 以下操作数据库的操作，开启作为一次事务
        with transaction.atomic():
            # 在数据库操作前，创建保存点（数据库最初的状态）
            save_id = transaction.savepoint()
            # 获取登录用户
            user = request.user
            # 获取订单编号：时间 + user_id == '2020123113041200000001'
            order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '{:0>9d}'.format(user.id)
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
                    # 每个商品都有多次下单的机会，直到库存不足
                    while True:
                        # 读取商品的sku信息
                        sku = SKU.objects.get(id=sku_id)  # 查询商品和库存信息时，不能出现缓存，所有不用 filter(id__in=sku_ids)
                        # 获取当前被勾选商品的库存
                        sku_count = new_cart_dict[sku.id]
                        # 获取sku商品原始的库存stock和销量sales
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # # 模型网络延迟
                        # import time
                        # time.sleep(5)
                        # 如果订单中的商品数量大于库存，响应库存不足
                        if sku_count > origin_stock:
                            # 库存不足，回滚
                            transaction.savepoint_rollback(save_id)
                            print(request.user, '库存不足')
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': err_msg[RETCODE.STOCKERR]})
                        # 如果库存满足，SKU 减库存，加销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        # 如果在更新数据时，原始数据变化了，那么返回0，表示有资源抢夺
                        if result == 0:
                            # 由于其他用户提前对该商品完成下单，该商品此次下单失败，重新进行下单
                            continue
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
                        # 该件商品下单成功，退出循环
                        break
                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            # 对于未知的数据库错误，暴力回滚
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
        else:
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
