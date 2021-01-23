# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date, timedelta
from rest_framework.response import Response

from users.models import User
from goods.models import GoodsVisitCount
from meiduo_admin.serializers.statistical import GoodsDayVisitSerializer


class BaseUserStatisticsView(APIView):
    """用户数据统计类"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 获取当天日期
        self.meiduo_now_date = date.today()

    def get(self, request):
        """获取并返回用户总量与当天日期"""
        # 获取统计数据
        data = self.get_statistics()
        # 返回统计数据
        return self.build_statistics(data=data)

    def get_statistics(self):
        """获取统计数据"""
        data = self.get_user_data()
        if data == -1:
            raise NotImplementedError('获取所需用户数量未完成')
        return data

    def build_statistics(self, data):
        """构造统计数据"""
        return Response({
            'date': self.meiduo_now_date,
            'count': data
        })

    def get_user_data(self, *args, **kwargs):
        """按照业务需要，获取用户数量，子类必须完成该方法"""
        return -1


class UserCountView(BaseUserStatisticsView):
    """用户数量统计"""

    def get_user_data(self):
        """获取用户总量"""
        return User.objects.all().count()


class UserDayIncrementView(BaseUserStatisticsView):
    """日增用户数量统计"""

    def get_user_data(self):
        """获取当天日增用户总量"""
        return User.objects.filter(date_joined__gte=self.meiduo_now_date).count()


class UserDayActiveView(BaseUserStatisticsView):
    """日活用户数量统计"""

    def get_user_data(self):
        """获取当天登录用户总量"""
        return User.objects.filter(last_login__gte=self.meiduo_now_date).count()


class UserDayOrdersView(BaseUserStatisticsView):
    """日下单用户"""

    def get_user_data(self, *args, **kwargs):
        """获取当天下单用户总量"""
        return len(set(User.objects.filter(orderinfo__create_time__gte=self.meiduo_now_date)))


class UserMonthPerDayView(BaseUserStatisticsView):
    """每月日增用户统计"""

    def build_statistics(self, data):
        """返回每月日增用户统计数据"""
        return Response(data)

    def get_user_data(self, *args, **kwargs):
        """获取一个月内每一天日增用户的数量"""
        # 获取一个月前的日期
        month = 30
        month_ago_date = self.meiduo_now_date - timedelta(days=month-1)
        day_user_count_list = []
        # 获取每一天内的日增用户
        for i in range(month):
            begin_day = month_ago_date + timedelta(days=i)
            end_day = begin_day + timedelta(days=1)
            count = User.objects.filter(date_joined__gte=begin_day, date_joined__lt=end_day).count()
            day_user_count_list.append({
                'count': count,
                'date': begin_day,
            })
        return day_user_count_list


class GoodsDayVisitView(BaseUserStatisticsView):
    """日商品访问量"""

    def get_user_data(self, *args, **kwargs):
        """获取当天所有商品的访问量"""
        goods = GoodsVisitCount.objects.filter(date__gte=self.meiduo_now_date)
        goods_seq = GoodsDayVisitSerializer(goods, many=True)
        return goods_seq.data


if __name__ == '__main__':
    pass
