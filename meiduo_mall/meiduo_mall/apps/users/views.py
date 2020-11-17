from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from django.views import View


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
        # 判断参数是否齐全
        # 判断用户名是否是5-20个字符
        # 判断密码是否是8-20个字符
        # 判断两次输入密码是否一致
        # 判断手机号是否合法
        # 判断用户是否勾选了协议
        # 保存注册数据：注册业务的核心
        # 返回响应结果

        return HttpResponse('ha')
