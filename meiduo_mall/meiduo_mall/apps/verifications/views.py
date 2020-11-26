from django.views import View
import random
import string
from django import http
from django.views import View
from django_redis import get_redis_connection
import logging
from django.db import DatabaseError

from meiduo_mall.utils import constants
from meiduo_mall.utils.response_code import RETCODE, err_msg
from verifications.libs.captcha.captcha import captcha
from verifications.libs.yuntongxun.ccp_sms import CCP
from celery_tasks.sms.tasks import send_sms_code


logger = logging.getLogger('django')


class SMSCodeView(View):
    """接收图形验证码并验证，验证通过后发送短信验证码"""

    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号码
        :return: JSON --> {code：errmsg}
        """
        # 接收参数
        image_code_user = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数
        # mobile不需要校验，因为路由中已经校验过了
        # image_code_client不需要二次校验，因为后面会对比用户输入的图形验证码
        # uuid也不需要二次校验，因此后面会通过uuid提取redis中的图形验证码
        if not all([image_code_user, uuid]):
            return http.HttpResponseForbidden('缺少必要参数')
        try:
            # 连接Redis数据库
            redis_conn = get_redis_connection('verify_code')
            # 判断60秒内是否频繁发送短信验证码，如果能从Redis中获取到数据，那么就是过于频繁
            if redis_conn.get('send_sms_flag_{}'.format(mobile)):
                return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': err_msg[RETCODE.THROTTLINGERR]})
            # 获取Redis数据库中图形验证码
            image_code_redis = redis_conn.get('img_{}'.format(uuid))
            # 判断图形验证码是否过期，如果过期，返回值为None
            if image_code_redis is None:
                return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': err_msg[RETCODE.IMAGECODEERR]})
            # 删除图形验证码
            redis_conn.delete('img_{}'.format(uuid))
            image_code_redis = image_code_redis.decode('utf-8')  # redis接收类型为bytes类型，将bytes类型转为字符串
        except DatabaseError:
            return http.JsonResponse({'code': RETCODE.DATABASEERROR, 'errmsg': err_msg[RETCODE.DATABASEERROR]})
        # 对比图形验证码
        if image_code_redis.lower() != image_code_user.lower():  # 转换为小写，再比较
            return http.JsonResponse({'code': RETCODE.IMAGECODEXPIRED, 'errmsg': err_msg[RETCODE.IMAGECODEXPIRED]})
        # 生成短信验证码，随机6位数字
        sms_code = ''.join(random.choices(string.digits, k=6))

        # # 保存短信验证码，过期时间5分钟
        # redis_conn.setex('sms_{}'.format(mobile), constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # # 保存60s内是否重复发送短信验证码的标识
        # redis_conn.setex('send_sms_flag_{}'.format(mobile), constants.SEND_SMS_CODE_INTERVAL, 'No')
        try:
            # 创建redis管道
            pl = redis_conn.pipeline()
            # 将命令添加进队列中
            # 保存短信验证码，过期时间5分钟
            pl.setex('sms_{}'.format(mobile), constants.SMS_CODE_REDIS_EXPIRES, sms_code)
            # 保存60s内是否重复发送短信验证码的标识
            pl.setex('send_sms_flag_{}'.format(mobile), constants.SEND_SMS_CODE_INTERVAL, 'No')
            # 执行所有命令
            pl.execute()
        except DatabaseError:
            return http.JsonResponse({'code': RETCODE.DATABASEERROR, 'errmsg': err_msg[RETCODE.DATABASEERROR]})
        # 手动输出日志，记录短信验证码
        logger.info('短信验证码:{}'.format(sms_code))
        # # 发送短信验证码
        # CCP().send_template_sms(to=mobile,
        #                         data=[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
        #                         tempId=constants.SEND_SMS_TEMPLATE_ID)
        # 使用Celery发送短信验证码
        send_sms_code.delay(mobile, sms_code)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class ImageCodeView(View):
    """生成并图形验证码"""
    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别码，用于唯一标识该图形验证属于哪个用户的
        :return: image/jpg
        """

        # 主体业务逻辑：生成、保存图形验证码
        # 生成图形验证码
        text, image = captcha.generate_captcha()
        try:
            # 保存图形验证码，Redis的2号库，过期时间5分钟
            redis_conn = get_redis_connection('verify_code')
            redis_conn.setex('img_{}'.format(uuid), constants.IMAGE_CODE_REDIS_EXPIRES, text)
        except DatabaseError:
            return http.HttpResponse(err_msg[RETCODE.DATABASEERROR])
        # 响应图形验证码
        return http.HttpResponse(image, content_type='image/jpg')
