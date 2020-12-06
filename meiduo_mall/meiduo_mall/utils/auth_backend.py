# -*- coding: UTF-8 -*-
"""自定义用户认证后端"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from django import http
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

from users.models import User
from meiduo_mall.utils.response_code import RETCODE, err_msg
from meiduo_mall.utils import constants


def generate_email_verify_url(user):
    """
    生成认证邮箱链接
    :param user: 当前用户
    :return http://www.meiduo.site/emails/verification/?token=eysdjflkdsfjsdlkgjasgOIUDSOGJSjdlskf
    """
    sq = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = sq.dumps(data)
    return settings.EMAIL_VERIFY_URL + '?token=' + token.decode()


class LoginRequiredJsonMixin(LoginRequiredMixin):
    """自定义判断用户是否登录的扩展类：用来返回JSON类型数据，默认只能返回HTML页面"""
    def handle_no_permission(self):
        """
        直接响应json数据


        LoginRequiredMixin源码：
        >>> class AccessMixin
        >>>     ...
        >>>     def handle_no_permission(self):
        >>>         if self.raise_exception:
        >>>             raise PermissionDenied(self.get_permission_denied_message())
        >>>     return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


        >>> class LoginRequiredMixin(AccessMixin):
        >>>     def dispatch(self, request, *args, **kwargs):
        >>>         if not request.user.is_authenticated:
        >>>             return self.handle_no_permission()
        >>>         return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)

        """
        # 只需要重写handel_no_permission，不需要重写 dispatch
        # 因为判断用户是否登录的操作，父类LoginRequiredMixin已经完成，子类只需要关心，如果用户未登录，对应怎样的操作
        return http.JsonResponse({'code': RETCODE.SESSIONERR, 'errmsg': err_msg[RETCODE.SESSIONERR]})


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
    """自定义用户登录认证后端，实现手机号与用户名都可作为账号进行验证，默认只能通过用户名作为账号进行验证"""
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
