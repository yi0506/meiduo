# -*- coding: UTF-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings

from meiduo_mall.utils import constants


def encrypt_openid(openid):
    """对openid进行加密(序列化)"""
    # 创建序列化器对象
    sq = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.OPENID_EXPIRES)
    # 待序列化的数据
    data = {'openid': openid}
    # 数据序列化
    token = sq.dumps(data)
    # 返回序列化后(加密)的数据
    return token.decode()


if __name__ == '__main__':
    pass
