# -*- coding: UTF-8 -*-
from rest_framework import serializers

from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'password': {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        """重写保存数据方法"""
        # 添加管理员字段
        validated_data['is_staff'] = True
        # 调用父类方法创建管理员用户
        admin = super().create(validated_data)
        # 用户密码加密
        password = validated_data['password']
        admin.set_password(password)
        admin.save()
        return admin

    def update(self, instance, validated_data):
        """重写更新方法"""
        # 更新字段
        user = super(AdminSerializer, self).update(instance, validated_data)
        # 对密码进行加密
        user.set_password(validated_data['password'])
        user.save()
        return user
