from django.shortcuts import render, redirect
from django import http
import re
from django.urls import reverse
from django.views import View
from django.db import DatabaseError
from django.contrib.auth import login, authenticate, logout
from django_redis import get_redis_connection
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import logging

from meiduo_mall.utils.response_code import RETCODE, err_msg
from users.models import User, Address  # 这里可以直接从users开始导入，是由于添加了导包路径
from meiduo_mall.utils import constants
from meiduo_mall.utils.auth_backend import LoginRequiredJsonMixin, generate_email_verify_url, check_email_verify_token
from celery_tasks.email.tasks import send_verify_email


logger = logging.getLogger('django')


class ChangePasswordView(LoginRequiredMixin, View):
    """修改密码"""

    def get(self, request):
        """展示修改密码界面"""
        return render(request, 'user_center_pass.html')

    def post(self, request):
        """实现修改密码逻辑"""
        # 接收参数
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')
        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            if request.user.check_password(old_password) is False:
                return render(request, 'user_center_pass.html', {'origin_password_errmsg': '原始密码错误'})
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'origin_password_errmsg': '修改密码失败'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')
        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return render(request, 'user_center_pass.html', {'change_password_errmsg': '修改密码失败'})
        # 清理状态保持信息
        logout(request)
        response = redirect(reverse('users:login'))
        response.delete_cookie('username')
        # # 响应密码修改结果：重定向到登录界面
        return response


class UpdateTitleAddressView(LoginRequiredJsonMixin, View):
    """更新地址标题"""
    def put(self, request, address_id):
        """更新地址标题逻辑"""
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        # 校验参数
        if not title:
            return http.HttpResponseForbidden('缺少title参数')
        try:
            # 查询要更新标题的地址
            address = Address.objects.get(id=address_id)
            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
        else:
            # 响应更新标题结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class DefaultAddressView(LoginRequiredJsonMixin, View):
    """设置默认地址"""
    def put(self, request, address_id):
        """实现默认设置地址逻辑"""

        try:
            # 查询出要将哪个地址作为默认地址
            address = Address.objects.get(id=address_id)
            # 将指定地址设置为默认地址
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
        else:
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class UpdateDeleteAddressView(LoginRequiredJsonMixin, View):
    """更新和删除地址"""
    def put(self, request, address_id):
        """更新地址"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        # 使用最新的地址信息覆盖指定的旧的地址信息
        try:
            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
            address = Address.objects.get(id=address_id)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
        else:
            # 响应新的地址信息给前端
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            # 响应新增地址结果：需要将新增的地址返回给前端渲染
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'address': address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        # 实现指定地址的逻辑删除：is_delete=True
        try:
            Address.objects.filter(id=address_id).update(is_deleted=True)
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
        else:
            # 响应结果： code、errmsg
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class AddressCreateView(LoginRequiredJsonMixin, View):
    """新增收货地址"""
    def post(self, request):
        """实现新增地址逻辑"""
        # 判断用户地址是否超过上限：查询当前登录用户的地址数量
        # addr_count = Address.objects.filter(user=request.user).count()  # 直接查询
        addr_count = request.user.addresses.count()  # 关联查询，"addresses" 为 related_name 关联字段
        if addr_count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': err_msg[RETCODE.THROTTLINGERR]})
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('参数mobile有误')
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')
        # 保存用户输入的地址信息
        try:
            address = Address.objects.create(
                user=request.user,  # 对外键赋值 模型类对象，django会自动获取其主键id，并添加到 模型类对象_id 字段中
                title=receiver,  # 标题默认为收货人，产品需求决定
                receiver=receiver,
                province_id=province_id,  # 直接对外键赋值 模型类对象_id
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email,
            )
            # 如果当前登录用户没有默认收货地址，则需要指定默认地址，将当前新建的地址作为默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': err_msg[RETCODE.DBERR]})
        else:
            # 新增地址成功，将新增的地址响应给前端实现局部刷新
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            # 响应新增地址结果：需要将新增的地址返回给前端渲染
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'address': address_dict})


class AddressView(LoginRequiredMixin, View):
    """用户收货地址"""
    def get(self, request):
        """查询并展示用户地址信息页面"""
        # 获取当前登录用户对象
        login_user = request.user
        # 查询地址信息，以当前登录用户和is_deleted=False为条件查询地址信息
        address_model_list = Address.objects.filter(user=login_user, is_deleted=False)
        # 将用户模型列表转为字典列表，Vue.js和JsonResponse不认识模型列表，
        # 如果使用Django或jinja2模板引擎，则可以直接使用
        address_list = []
        for address in address_model_list:
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }
            address_list.append(address_dict)
        context = {
            # 'default_address_id': login_user.default_address_id,  # 没有默认地址时为 None
            'default_address_id': login_user.default_address_id or '-1',  # 没有默认地址时为 '-1'，收货地址id从1开始
            'addresses': address_list,
        }
        return render(request, 'user_center_site.html', context)


class VerifyUseEmail(View):
    """验证用户邮箱"""
    def get(self, request):
        # 接收参数
        token = request.GET.get('token')
        # 校验参数
        if not token:
            return http.HttpResponseForbidden('缺少token')
        # 从token中提取用户信息user_id
        user = check_email_verify_token(token=token)
        if user is None:
            return http.HttpResponseBadRequest('无效的token')
        # 将该用户的email_active字段置为True
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('激活邮箱失败')
        else:
            # 响应结果：从定向到用户中心
            return redirect(reverse('users:info'))


class EmailView(LoginRequiredJsonMixin, View):
    """添加邮箱"""

    def put(self, request):
        """添加邮箱到数据库中，能够进入到路由函数，说明用户已经通过LoginRequiredJsonMixin认证，已经登录"""
        # 接收参数
        json_str = request.body.decode()
        json_dict = json.loads(json_str)
        email = json_dict.get('email')
        # 校验参数
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden('参数email有误')
        # 用户已登录，将邮箱保存到对应用户的数据库email字段中
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.EMAILERR, 'errmsg': err_msg[RETCODE.EMAILERR]})
        else:
            # 发送验证邮件
            verify_url = generate_email_verify_url(request.user)
            send_verify_email.delay(to_email=email, verify_url=verify_url)  # 一定要调用delay
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class UserInfoView(LoginRequiredMixin, View):
    """用户中心"""
    def get(self, request):
        """
        提供用户中心页面
            检测用户是否登录: LoginRequiredMixin，会帮我们完成这件事, 该功能的实现必须继承自 LoginRequiredMixin 类
            当用户已经登录，则进入用户中心页面
            如果用户未登录，则跳转到登录页面，登录成功后直接跳转到用户中心页面
        """
        # login_url 默认为None，需要修改为 login_url = '/login/'，并且改为全局设置，在dev.py文件中配置: LOGIN_URL = '/login/
        # redirect_field_name = REDIRECT_FIELD_NAME = 'next' ，默认不需要修改

        # 想要自动实现以下功能，必须继承 LoginRequiredMixin 类，不继承，就没有自动添加 next 参数的效果
        # 因为 UserInfoView 继承了 LoginRequiredMixin， 所以只有访问 "用户中心" 界面时( /info/ )，才会执行以下逻辑：
        #     检测用户是否登录，如果用户未登录，
        #           1. Django会重定向发送 login_url 中定义的url请求，此项目中 login_url 指向 "登录页面"( /login/ )
        #           2. 并且Django会在此次请求中自动增加一个 next=/info/ 的参数 ，最终请求变为 ---> 127.0.0.1/login/?next=/info/
        #           3. 用户进行登录后，将请求发送给 /login/ 指向的视图函数(我们定义的类视图 LoginView)，并且该请求包含一个查询字符串参数 ?next=/info/
        #      如果用户已经登录，
        #            则直接跳转到用户中心(/info/)

        # 我们需要再 LonginView 中增加以下的逻辑：
        #       当url参数中有next ---> 127.0.0.1:8000/login/?next=/info/ 则提取出来，登录成功后跳转到 127.0.0.1:8000/info/ 指向的页面
        #       如果url参数没有next ---> 127.0.0.1:8000/login/ 则登陆成功后，直接跳转到首页 127.0.0.1:8000/

        # 只要能够进入该视图，那么就是通过 LoginRequiredMixin 的认证，即用户已经登录过了
        # request中自带一个user对象的属性，如果用户已登录，那么 request.user 就指代已登录用户，可以直接使用 request.user.username 取出用户数据，不需要在通过查表获取数据了，
        # 如果用户未登录，那么该user对象为一个匿名用户，无法获取用户数据

        context = {
            'username': request.user.username,
            'mobile': request.user.mobile,
            'email': request.user.email,
            'email_active': request.user.email_active,
        }
        return render(request, 'user_center_info.html', context)


class LogoutView(View):
    """用户退出登录"""
    def get(self, request):
        """实现用户退出登录的逻辑"""
        # 清除状态保持信息
        logout(request)
        # 退出登录后，重定向到首页
        response = redirect(reverse('contents:index'))
        # 删除cookie中的username
        response.delete_cookie('username')
        return response


class LoginView(View):
    """用户登录"""

    def get(self, request):
        """提供用户登录页面"""
        return render(request, 'login.html')

    def post(self, request):
        """实现用户登录的逻辑"""
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 校验参数
        if not all([username, password]):
            return http.HttpResponseForbidden('缺少必传参数')
        if not re.search(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('请输入正确的用户名或手机号')
        if not re.search(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        # 认证用户：使用账号查询用户是否存在，如果用户存在，再校验密码是否正确
        user = authenticate(username=username, password=password)
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '账号或密码错误'})
        # 状态保持
        login(request=request, user=user)
        # 使用rememebered确定状态保持的时间（实现记住登录）
        if remembered != 'on':
            # 没有记住登录：状态保持在浏览器关闭后会话结束，session就销毁
            request.session.set_expiry(0)  # 单位是秒
        else:
            # 记住登录：设置状态保持时间为1小时，默认为None，表示两周
            request.session.set_expiry(constants.REMEMBERED_EXPIRES)
        # 取出next参数，返回一个字符串
        _next = request.GET.get('next')
        if _next:
            # 如果next有值，重定向到next指向的页面
            response = redirect(_next)
        else:
            # 如果next没有值，重定向的首页
            response = redirect(reverse('contents:index'))
        # 为了实现在首页右上角展示用户名信息，需要将用户名缓存到cookie中
        # 如果cookie中有username字段，则显示用户名
        # 如果没有，则显示未登录状态
        # 该逻辑由前端Vue模板引擎渲染，获取cookie中的username
        response.set_cookie('username', user.username, max_age=constants.REMEMBERED_EXPIRES)

        # 返回响应结果
        return response


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
        except Exception as e:
            logger.error(e)
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
            response = redirect(reverse('contents:index'))
            # 为了实现在首页右上角展示用户名信息，需要将用户名缓存到cookie中
            response.set_cookie('username', user.username, max_age=constants.REMEMBERED_EXPIRES)
            return response
