from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
import logging

from meiduo_mall.utils.response_code import RETCODE, err_msg


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
            oauth.get_open_id(access_token=access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('oauth2.0认证失败')
        # 使用openid判断该QQ用户是否绑定过美多商城
        # 返回响应
        return http.HttpResponse('e')


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
