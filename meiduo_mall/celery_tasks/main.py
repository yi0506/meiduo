# -*- coding: UTF-8 -*-
""" Celery入口 """
from celery import Celery


# 创建Celery实例（生产者）
celery_app = Celery('meiduo')

# 加载配置
celery_app.config_from_object('celery_tasks.config')


if __name__ == '__main__':
    pass
