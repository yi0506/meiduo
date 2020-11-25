from django.shortcuts import render, redirect
from django import http
import re
from django.urls import reverse
from django.views import View
from django.db import DatabaseError
from django.contrib.auth import login
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE, err_msg
from users.models import User  # 这里可以直接从users开始导入，是由于添加了导包路径


class MobileCountView(View):
    """判断手机号是否重复注册"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'count': count})


class UserNameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        使用查询字符串的方式，会自动通过url的正则匹配去校验参数，因此不需要校验参数，直接实现主体业务逻辑

        :param request: 请求报文
        :param username: 用户名
        :return: json
        """
        # 实现主体业务逻辑：使用username查询对应的记录的条数(filter返回的是符合条件的查询集)
        count = User.objects.filter(username=username).count()
        # 返回响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'count': count})


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """提供用户注册页面"""
        return render(request, 'register.html')

    def post(self, request):
        """实现用户注册业务逻辑"""

        # 接收参数：表单参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        password2 = request.POST.get('password2')
        sms_code_user = request.POST.get('sms_code')
        allow = request.POST.get('allow')

        # 校验参数：前后端的校验需要分开，避免恶意用户越过前端逻辑发送请求，要保证后端的安全，前后端的校验逻辑相同
        # 如果不满足条件，那么返回错误信息
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow, sms_code_user]):
            return http.HttpResponseForbidden('缺少必要参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseForbidden('请勾选用户协议')
        try:
            # 校验短信验证码
            redis_conn = get_redis_connection('verify_code')
            sms_code_redis = redis_conn.get('sms_{}'.format(mobile))
            if sms_code_redis is None:  # 判断短信验证码是否过期
                return render(request, 'register.html', {'sms_code_errmsg': '短信验证码已失效'})
            if sms_code_redis.decode('utf-8') != sms_code_user:
                return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        except DatabaseError:
            return render(request, 'register.html', {'sms_code_errmsg': err_msg[RETCODE.DATABASEERROR]})
        # 保存注册数据：注册业务的核心
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_error_msg': '注册失败'})
        else:
            # 美多商城项目逻辑：注册成功即登陆成功，因此注册完成后自动登录，跳转到首页
            # 登录的本质就是状态保持
            # 实现状态保持
            login(request, user)
            # 返回响应结果，重定向的首页
            return redirect(reverse('contents:index'))
