from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
import logging
from django.contrib.auth import login

from meiduo_mall.utils.response_code import RETCODE, err_msg
from oauth.models import OAuthQQUser
from meiduo_mall.utils import constants
from meiduo_mall.utils.encryption import encrypt_openid


logger = logging.getLogger('django')


class QQAuthCallBackView(View):
    """处理QQ登录回调"""

    def get(self, request):
        """获取authorization code，返回access token"""
        # 获取authorization code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败，请重试')
        # 创建oauth对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET, redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            # 使用authorization code获取access token
            access_token = oauth.get_access_token(code)
            # 使用access token获取open id
            openid = oauth.get_open_id(access_token=access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('oauth2.0认证失败')
        # 使用openid判断该QQ用户是否绑定过美多商城
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # openid未绑定美多商城用户
            # 加密openid
            openid = encrypt_openid(openid)
            context = {'access_token_openid': openid}
            return render(request, 'oauth_callback.html', context)
        else:
            # openid已经绑定美多商城用户
            # oauth_user.user表示从QQ登录模型类对象的外键中找到对应的用户模型类对象
            login(request=request, user=oauth_user.user)
            # 重定向到首页
            response = redirect(reverse('contents:index'))
            # 状态保持：将用户名写入到cookies中
            response.set_cookie('username', oauth_user.user, constants.REMEMBERED_EXPIRES)
            return response


class QQAuthURLView(View):
    """提供QQ登录扫码页面"""

    def get(self, request):
        """
        提供qq登录扫码页面
        :return json
        """
        # 接受参数 next
        _next = request.GET.get('next')
        # 创建oauth对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=_next)
        # 生成QQ登录扫码链接地址
        login_url = oauth.get_qq_url()
        # 返回响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'login_url': login_url})
