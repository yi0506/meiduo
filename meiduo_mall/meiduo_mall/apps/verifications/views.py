from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
from meiduo_mall.utils import constants


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号码
        :return: JSON --> {code：errmsg}
        """
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数
        # mobile不需要校验，因为路由中已经校验过了
        # image_code_client不需要二次校验，因为后面会对比用户输入的图形验证码
        # uuid也不需要二次校验，因此后面会通过uuid提取redis中的图形验证码
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 接收图形验证码

        # 删除图形验证码

        # 对比图形验证码

        # 生成短信验证码

        # 保存图形验证码
        # 发送短信验证码

        # 响应结果


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别码，用于唯一标识该图形验证属于哪个用户的
        :return: image/jpg
        """

        # 主体业务逻辑：生成、保存图形验证码
        # 生成图形验证码
        text, image = captcha.generate_captcha()

        # 保存图形验证码，Redis的2号库
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_{}'.format(uuid), constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')
