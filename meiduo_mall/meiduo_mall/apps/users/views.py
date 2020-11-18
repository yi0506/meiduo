from django.shortcuts import render, redirect
from django import http
import re
from django.urls import reverse
from django.views import View
from users.models import User
from django.db import DatabaseError


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
        allow = request.POST.get('allow')
        # 校验参数：前后端的校验需要分开，避免恶意用户越过前端逻辑发送请求，要保证后端的安全，前后端的校验逻辑相同
        self.check_param(username=username, password=password, password2=password2, mobile=mobile, allow=allow)
        # 保存注册数据：注册业务的核心
        user = self.save_user_data(username=username, password=password, mobile=mobile, request=request)
        # 返回响应结果，重定向的首页
        print(reverse('contents:index'), '首页路由')
        return redirect(reverse('contents:index'))

    @staticmethod
    def check_param(username, password, password2, mobile, allow):
        """校验参数，如果不满足条件，那么返回错误信息，403"""
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
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

    @staticmethod
    def save_user_data(username, password, mobile, request):
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_error_msg': '注册失败'})
        else:
            return user
