# -*- coding: UTF-8 -*-
"""定义任务"""
from logging import getLogger

from .yuntongxun.ccp_sms import CCP
from celery_tasks.utils import constants
from celery_tasks.main import celery_app


logger = getLogger('django')


# 使用装饰器装饰异步任务，保证celery能识别任务
# bind：保证task对象会作为第一个参数自动传入，task对象是当前任务的调用者
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@celery_app.task(bind=True, name='ccp_send_sms_code', retry_backoff=3)
def send_sms_code(self, mobile, sms_code):
    """
    发送短信验证码的异步任务
    :param self: 当前的task对象，只有写了bind=True，才能传self
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return 成功0，失败-1
    """
    # 发送短信验证码
    try:
        result = CCP().send_template_sms(to=mobile, data=[sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                         tempId=constants.SEND_SMS_TEMPLATE_ID)
    except Exception as e:
        logger.error(e)
        # 有异常自动重试三次
        raise self.retry(exc=e, max_retries=3)
    else:
        return result


if __name__ == '__main__':
    pass
