# -*- coding: UTF-8 -*-
"""
Celery入口
        生产者：meiduo_mall
        中间人：redis,使用redis作为任务队列，存放任务
        消费者：Celery
        任务：自己定义，如发送短信的任务
"""
from celery import Celery

# celery 默认使用多进程方式运行，进程之间相互独立，django进程和celery进程相互独立，默认情况下无法进行通信
# 所以celery进程在读取django进程的settings的环境变量时，找不到
# 解决方法：为celery配置一下django环境变量
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
# 创建Celery实例（生产者）
celery_app = Celery('meiduo')
# 加载配置
celery_app.config_from_object('celery_tasks.config')
# 注册异步任务，写任务包所在的位置，他会自动找到任务包下面的tasks.py文件，用一个列表传递所有的任务包！！！！！
# 让celery去监视这个消息队列中有没有任务，有就去执行，没有就等待
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])


if __name__ == '__main__':
    pass
