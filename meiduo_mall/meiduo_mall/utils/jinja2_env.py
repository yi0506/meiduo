# -*- coding: UTF-8 -*-
"""自定义jinja2环境配置文件"""
from jinja2 import Environment
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage


def jinja2_environment(**options):
    """自定义jinja2环境"""
    # 创建env对象
    env = Environment(**options)

    # 自定义jinja2模板语法，
    # 实现：
    #       {{ static('模板文件的相对路径') }} ---> src="{{ static('js/register.js') }}"
    #       {{ url(路由的命名空间) }}         ---> href="{{ url('users:register') }}"
    env.globals.update({

        # 根据填写的相对路径，拼接静态文件的完整路径
        # staticfiles_storage.url会自动获取静态文件所在目录(static文件夹)，所以相对路径只需要从static目录下开始写
        # staticfiles_storage.url会将前后路径进行拼接，得到完整静态文件路径
        'static': staticfiles_storage.url,

        # 重定向/反向解析
        'url': reverse,
    })
    # 返回env对象
    return env


if __name__ == '__main__':
    pass
