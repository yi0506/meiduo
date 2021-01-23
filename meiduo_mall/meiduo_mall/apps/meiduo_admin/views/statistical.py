# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date
from rest_framework.response import Response

from users.models import User


class UserStatisticsView(APIView):
    """用户数据统计类"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 获取当天日期
        self.meiduo_now_date = date.today()

    def get(self, request):
        """获取并返回用户总量与当天日期"""
        # 获取用户总量
        count = self.get_user_count()
        if count == -1:
            raise NotImplementedError('获取所需用户数量未完成')
        # 返回结果
        return Response({
            'date': self.meiduo_now_date,
            'count': count
        })

    def get_user_count(self, *args, **kwargs):
        """按照业务需要，获取用户数量"""
        return -1


class UserCountView(UserStatisticsView):
    """用户数量统计"""

    def get_user_count(self):
        """获取用户总量"""
        return User.objects.all().count()


class UserDayIncrementView(UserStatisticsView):
    """日增用户数量统计"""

    def get_user_count(self):
        """获取当天日增用户总量"""
        return User.objects.filter(date_joined__gte=self.meiduo_now_date).count()


class UserDayActiveView(UserStatisticsView):
    """日活用户数量统计"""

    def get_user_count(self):
        """获取当天登录用户总量"""
        return User.objects.filter(last_login__gte=self.meiduo_now_date).count()


if __name__ == '__main__':
    pass
