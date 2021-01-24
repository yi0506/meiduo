# -*- coding: UTF-8 -*-
def jwt_response_payload_handler(token, user=None, request=None):
    """重写jwt认证成功返回数据"""
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }


if __name__ == '__main__':
    pass
