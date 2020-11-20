from django.shortcuts import render
from django.views import View
from verifications.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from django import http
# Create your views here.


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
        redis_conn.setex('img_{}'.format(uuid), 300, text)

        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')
