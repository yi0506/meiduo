from django.shortcuts import render, redirect
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django import http
import logging
import re
from django_redis import get_redis_connection
from django.contrib.auth import login
from django.db import DatabaseError

from meiduo_mall.utils.response_code import RETCODE, err_msg
from oauth.models import OAuthQQUser
from meiduo_mall.utils import constants
from meiduo_mall.utils.auth_backend import encrypt_openid, decrypt_openid
from users.models import User
from meiduo_mall.utils.method_package import merge_cart_cookies_and_redis


logger = logging.getLogger('django')


class QQAuthCallBackView(View):
    """处理QQ登录回调"""

    def get(self, request):
        """获取authorization code，返回access token"""
        # 用户扫码后，QQ互联将authorization code返回给浏览器，
        # 让浏览器通过 QQ_REDIRECT_URI 携带authorization code进行重定向
        # http://127.0.0.1:8000/oauth_callback?code=authorization_code
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
            openid_encrypted = encrypt_openid(openid)
            context = {'access_token_openid': openid_encrypted}
            return render(request, 'oauth_callback.html', context)
        else:
            # openid已经绑定美多商城用户
            # oauth_user.user表示从QQ登录模型类对象的外键中找到对应的用户模型类对象
            login(request=request, user=oauth_user.user)
            # 重定向，从哪来回哪去，用户从哪个页面触发了需要注册的逻辑，就重定向到哪里去
            _next = request.GET.get('state')
            response = redirect(_next)
            # 状态保持：将用户名写入到cookies中
            response.set_cookie('username', oauth_user.user, constants.REMEMBERED_EXPIRES)
            # 用户登录成功，合并cookie购物车到redis购物车
            response = merge_cart_cookies_and_redis(request=request, user=oauth_user.user, response=response)
            return response

    def post(self, request):
        """实现用户的绑定"""
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code_client = request.POST.get('sms_code')
        openid_encrypted = request.POST.get('access_token_openid')

        # 校验参数
        # 判断参数是否齐全
        if not all([mobile, password, sms_code_client, openid_encrypted]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合格
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断短信验证码是否一致
        try:
            redis_conn = get_redis_connection('verify_code')
            sms_code_server = redis_conn.get('sms_%s' % mobile)
        except Exception as e:
            logger.error(e)
            return http.HttpResponse(err_msg[RETCODE.DATABASEERROR])
        else:
            if sms_code_server is None:
                return render(request, 'oauth_callback.html', {'sms_code_errmsg': '无效的短信验证码'})
            if sms_code_client != sms_code_server.decode():
                return render(request, 'oauth_callback.html', {'sms_code_errmsg': '输入短信验证码有误'})
        # 反序列化openid
        openid_decrypted = decrypt_openid(openid_encrypted)
        # 判断openid是否有效：openid使用itsdangerous序列化后，只有600秒有效期
        if openid_decrypted is None:
            return render(request, 'oauth_callback.html', {'openid_errmsg': 'openid已失效'})
        # 主体业务逻辑：绑定用户与openid
        # 使用手机号查询对应的用户是否存在
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 如果手机号对应的用户不存在，那么新建用户
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            # 如果手机号对应的用户存在，那么要校验密码
            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '手机号或密码错误'})
        try:
            # 将 新建用户/已存在用户 绑定到openid
            # qq_user = OAuthQQUser(user=user, openid=openid_decrypted)
            # qq_user.save()
            oauth_qq_user = OAuthQQUser.objects.create(user=user, openid=openid_decrypted)
        except DatabaseError as e:
            logger.error(e)
            return render(request, 'oauth_callback.html', {'qq_login_errmsg': '账号绑定失败'})
        # 实现状态保持,即登录
        login(request, oauth_qq_user.user)
        # 重定向，从哪来回哪去，用户从哪个页面触发了需要注册的逻辑，就重定向到哪里去
        _next = request.GET.get('state')
        response = redirect(_next)
        # cookie写入用户名
        response.set_cookie('username', oauth_qq_user.user.username)
        # 用户登录成功，合并cookie购物车到redis购物车
        response = merge_cart_cookies_and_redis(request=request, user=oauth_qq_user.user, response=response)
        # 响应结果
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
