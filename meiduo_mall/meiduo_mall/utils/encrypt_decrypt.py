# -*- coding: UTF-8 -*-
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from itsdangerous import BadData

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


def decrypt_eponid(token):
    """对openid进行反序列化(解密)"""
    # 创建序列化器对象
    sq = Serializer(secret_key=settings.SECRET_KEY, expires_in=constants.OPENID_EXPIRES)
    # 数据反序列化，得到openid
    try:
        data = sq.loads(token)
    except BadData:
        return None
    else:
        # 返回openid
        return data.get('openid')


if __name__ == '__main__':
    pass
