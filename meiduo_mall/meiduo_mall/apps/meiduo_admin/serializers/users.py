# -*- coding: UTF-8 -*-
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from users.models import User


class UserSerializer(ModelSerializer):
    """用户模型类序列化器"""
    mobile = serializers.RegexField(r'^1[3-9]\d{9}$')  # 验证手机号字段

    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email', 'password')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'max_length': 20,
                'min_length': 8,
            },
            'username': {
                'max_length': 20,
                'min_length': 5,
            }
        }

    def create(self, validated_data):
        """继承并重写create方法，对password进行加密"""
        # # 方法一：
        # user = super(UserSerializer, self).create(validated_data)
        # # 密码加密
        # user.set_password(validated_data['password'])
        # user.save()

        # 方法二：
        user = User.objects.create_user(**validated_data)
        return user


if __name__ == '__main__':
    pass
