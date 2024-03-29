# -*- coding: UTF-8 -*-
from django.core.mail import send_mail
from django.conf import settings
from logging import getLogger

from celery_tasks.main import celery_app


logger = getLogger('django')


@celery_app.task(bind=True, name='send_verify_email', retry_backoff=3)
def send_verify_email(self, to_email, verify_url):
    """发送验证邮箱任务"""
    subject = '美多商城邮箱验证'
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        # send_mail('邮件标题', '普通邮件正文', '发件人', '收件人列表', '多媒体邮件正文')
        send_mail(subject=subject, message='', from_email=settings.EMAIL_FROM, recipient_list=[to_email, ], html_message=html_message)
    except Exception as e:
        # 出现错误，重试3次
        logger.error(e)
        raise self.retry(exc=e, max_retries=3)


if __name__ == '__main__':
    pass
