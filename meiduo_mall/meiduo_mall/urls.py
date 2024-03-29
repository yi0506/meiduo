"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # users，总路由不校验，子路由校验
    url(r'^', include('users.urls', namespace='users')),
    # contents,总路由不校验，子路由校验
    url(r'^', include('contents.urls', namespace='contents')),
    # verifications,总路由不校验，子路由校验
    url(r'^', include('verifications.urls')),
    # oauth认证
    url(r'^', include('oauth.urls')),
    # areas
    url(r'^', include('areas.urls')),
    # goods
    url(r'^', include('goods.urls', namespace='goods')),
    # haystack
    url(r'^search/', include('haystack.urls')),
    # carts
    url(r'^', include('carts.urls', namespace='carts')),
    # orders
    url(r'^', include('orders.urls', namespace='orders')),
    # payment
    url(r'^', include('payment.urls', namespace='payment')),
    # meiduo_admin
    url(r'^meiduo_admin/', include('meiduo_admin.urls')),
]
