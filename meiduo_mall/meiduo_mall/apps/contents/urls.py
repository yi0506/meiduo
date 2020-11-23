# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # 浏览器会自动在路由的最后添加一个'/'，如果url路径参数中没有写的话

    # 首页的路由为'/' 但是不需要写，因为根路径'/'会被django在总路由匹配后自动去除后，进行路由匹配
    # 如果写成 r'^/$，那么路由就要写 http://127.0.0.1:8000// ，两个斜杠

    # django在总路由匹配过之后，会将总路由从整个url路径参数中删除，只留下后面的部分，在子应用路由中匹配，从'/'之前开始删除，包括'/'
    # 因为 根路径'/'在项目总路由中进行了匹配，django匹配成功后，会将'/'前面的路由自动去除掉
    # Django的路由是 头不写尾写
    url(r'^$', views.IndexView.as_view(), name='index'),

]

if __name__ == '__main__':
    pass
