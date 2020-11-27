# -*- coding: UTF-8 -*-
"""自定义用户认证后端"""
from django.contrib.auth.backends import ModelBackend
import re

from users.models import User


def get_user_by_account(account):
    """
    通过账号获取用户
    :param account: 用户名或手机号
    :return: user
    """
    # 判断username是用户名还是手机号
    try:
        if re.search(r'^1[3-9]\d{9}$', account):
            # account == 手机号
            user = User.objects.get(mobile=account)
        else:
            # account == 用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class LoginAuthBackend(ModelBackend):
    """用户登录认证后端"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写用户认证的方法
        :param request: 请求报文
        :param username: 用户名或手机号
        :param password: 密码-明文
        :param kwargs: 额外参数
        :return: user
        """
        # 查询用户,校验密码
        user = get_user_by_account(username)
        if user is not None and user.check_password(password) is True:
            return user
        else:
            return None


if __name__ == '__main__':
    pass
