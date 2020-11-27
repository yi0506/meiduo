from django.shortcuts import render, redirect
from django.views import View
from django.contrib.staticfiles.storage import staticfiles_storage
# Create your views here.


class IndexView(View):
    """首页广告"""

    def get(self, request):
        """提供首页广告页面"""
        return render(request, 'index.html')


class FaviconView(View):
    """favicon图标"""

    def get(self, request):
        """提供favicon图标"""
        return redirect(staticfiles_storage.url('favicon.ico'))
