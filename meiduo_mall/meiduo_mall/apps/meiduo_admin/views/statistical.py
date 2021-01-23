# -*- coding: UTF-8 -*-
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from datetime import date
from rest_framework.response import Response

from users.models import User


class UserCountView(APIView):
    """用户数量统计"""
    # 权限指定
    permission_classes = [IsAdminUser]

    def get(self, request):
        """获取并返回用户总量与当天日期"""
        # 获取当天日期
        now_date = date.today()
        # 获取用户总量
        count = User.objects.all().count()
        # 返回结果
        return Response({
            'date': now_date,
            'count': count
        })





if __name__ == '__main__':
    pass
