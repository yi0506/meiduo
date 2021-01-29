# -*- coding: UTF-8 -*-
"""自定义用户认证后端与相关功能函数"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from django import http
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

from users.models import User
from meiduo_mall.utils.response_code import RETCODE, err_msg
from meiduo_mall.utils import constants


def check_email_verify_token(token):
    """反序列化token，获取user"""
    sq = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = sq.loads(token)
    except BadData:
        return None
    else:
        # 取出user_id 和 email
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


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


def encrypt_openid(openid):
    """对openid进行加密(序列化)"""
    # 创建序列化器对象
    sq = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.OPENID_EXPIRES)
    # 待序列化的数据
    data = {'openid': openid}
    # 数据序列化
    token = sq.dumps(data)
    # 返回序列化后(加密)的数据
    return token.decode()


def decrypt_openid(token):
    """对openid进行反序列化(解密)"""
    # 创建序列化器对象
    sq = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.OPENID_EXPIRES)
    # 数据反序列化，得到openid
    try:
        data = sq.loads(token)
    except BadData:
        return None
    else:
        # 返回openid
        return data.get('openid')


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
        # 判断用户为前台登录还是后台登录
        if request is None:
            # 通过后台登录
            try:
                # 查询是否存在该超级管理员用户
                user = User.objects.get(is_staff=True, username=username)
            except User.DoesNotExist:
                return None
            else:
                if user.check_password(password):
                    return user
        else:
            # 通过前台登录
            # 查询用户,校验密码
            user = get_user_by_account(username)
            if user is not None and user.check_password(password) is True:
                return user
            else:
                return None


if __name__ == '__main__':
    pass
