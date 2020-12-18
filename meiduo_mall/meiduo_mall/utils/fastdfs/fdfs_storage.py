# -*- coding: UTF-8 -*-
from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义存储类"""
    # def __init__(self, option=None):
    #     """初始化设置"""
    #     if not option:
    #         option = settings.CUSTOM_STORAGE_OPTIONS

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用，必须重写，文档要求
        :param name: 文件路径
        :param mode: 文件打开方式
        """
        # 该文件存储类，只完成文件的下载，不需要打开文件，因此不需要完成该功能，只需要pass
        pass

    def _save(self, name, content):
        """
        保存文件时被调用，文档要求，必须重写
        PS: 将来的后台管理系统中，需要在这个方法中实现文件上传到FastDFS服务器
        :param name: 文件路径
        :param content: 文件的二进制内容
        """
        # 不需要完成该功能，原因同上
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件的相对路径
        :return 文件的全路径
                http://192.168.192.133:8888/group1/M00/00/01/CtM3BVrMexWAfodJAAAhg8MeEWU8364862
        """
        return 'http://192.168.192.133:8888/' + name


if __name__ == '__main__':
    pass
