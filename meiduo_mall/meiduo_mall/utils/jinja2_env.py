# -*- coding: UTF-8 -*-
"""自定义jinja2环境配置文件"""
from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage


def jinja2_environment(**options):
    """自定义jinja2环境"""
    # 创建env对象
    env = Environment(**options)
    # 自定义jinja2模板语法，实现： {{ static('模板文件的相对路径') }}  {{ url(路由的命名空间) }}
    # src="{{ static('js/register.js') }}"
    env.globals.update({
        'static': staticfiles_storage.url,  # 获取静态文件路径的前缀，staticfiles_storage.url会读到静态文件(static)目录，相对路径只需要从static目录下开始写
        'url': reverse,  # 重定向/反向解析
    })
    # 返回env对象
    return env


if __name__ == '__main__':
    pass
