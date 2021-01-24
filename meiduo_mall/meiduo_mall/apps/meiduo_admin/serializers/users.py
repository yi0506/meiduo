# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer

from users.models import User


class UserSerializer(ModelSerializer):
    """用户模型类序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email')


if __name__ == '__main__':
    pass
