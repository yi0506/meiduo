# -*- coding: UTF-8 -*-
"""Celery配置文件"""
from celery_tasks.utils.db_ip import get_db_ip

# 指定中间人（消息队列、任务队列、容器）
# 这里的中间人使用redis数据库
broker_url = 'redis://:211314@{}:6379/10'.format(get_db_ip())


if __name__ == '__main__':
    pass
