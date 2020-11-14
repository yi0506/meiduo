from django.shortcuts import render

# Create your views here.
from django.views import View


class RegisterView(View):
    """用户注册"""

    def get(self, request):
        """提供用户注册页面"""
        return render(request, 'register.html')

    def post(self, requset):
        """获取用户注册信息"""
        pass
