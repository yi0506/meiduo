from django.shortcuts import render
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http

from meiduo_mall.utils.response_code import RETCODE, err_msg

# Create your views here.


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
