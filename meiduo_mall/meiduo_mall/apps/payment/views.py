from django.shortcuts import render
from django.views import View
from alipay import AliPay
from django.conf import settings
import os
from django import http
import re

from meiduo_mall.utils.auth_backend import LoginRequiredJsonMixin
from orders.models import OrderInfo
from meiduo_mall.utils.response_code import RETCODE, err_msg


class PaymentView(LoginRequiredJsonMixin, View):
    """对接支付宝支付"""
    def get(self, request, order_id):
        """
        :param request: 请求
        :param order_id: 订单id
        :return: Json
        """
        # 查询要支付的订单
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单信息错误')
        # 读取秘钥
        app_private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem")
        alipay_public_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem")
        with open(app_private_key_path, encoding='utf-8') as f:
            app_private_key_string = f.read()
        with open(alipay_public_key_path, encoding='utf-8') as f:
            alipay_public_key_string = f.read()
        # 创建对接支付宝接口的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url，如果才用同步通知就不传
            # 应用的私钥和支付宝公钥路径
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # 加密方式
            debug=settings.ALIPAY_DEBUG  # 指定是否为开发环境
        )
        # SDK对象对接支付宝的接口，获得登录页网址
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 订单支付总金额
            subject="美多商城%s" % order_id,  # 订单标题
            return_url=settings.ALIPAY_RETURN_URL,  # 同步通知的回调地址，如果不是同步通知，就不传
        )
        # 拼接完整的支付宝登录页网址
        # 电脑网站支付网关(生产环境)：https://openapi.alipay.com/gateway.do? + order_string
        # 电脑网站支付网关(沙箱环境)：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'alipay_url': alipay_url})
