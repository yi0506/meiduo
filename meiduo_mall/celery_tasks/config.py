# -*- coding: UTF-8 -*-
"""Celery配置文件"""
from django.conf import settings

# 指定中间人（消息队列、任务队列、容器）
# 这里的中间人使用redis数据库
# broker_url = 'redis://:211314@{}:6379/10'.format(settings.MEIDUO_DB_IP)
# 使用RabbitMQ作为中间人
broker_url = 'amqp://admin:211314@{}:5672'.format(settings.MEIDUO_DATABASE_IP)


if __name__ == '__main__':
    pass
