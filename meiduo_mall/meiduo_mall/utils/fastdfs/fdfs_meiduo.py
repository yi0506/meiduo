# -*- coding: UTF-8 -*-
import os
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFS_Client_Meiduo(object):
    """fdfs_client单例类"""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(FDFS_Client_Meiduo, cls).__new__(cls)
            cls._instance.client = Fdfs_client(settings.FDFS_CONF_PATH)
        # 返回单例
        return cls._instance

    def upload(self, image):
        """
        上传图片
        :param image: 文件对象
        :return 上传成功：文件远程地址，上传失败："error"
        """
        # 上传图片
        res = self.client.upload_by_buffer(image.read())
        # 判断是否上传成功
        if res['Status'] != 'Upload successed.':
            return 'Failed!'
        else:
            return res['Remote file_id'].replace('\\', '/')


if __name__ == '__main__':
    if os.getenv('DJANGO_SETTINGS_MODULE') is None:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'
    fd_meiduo = FDFS_Client_Meiduo()
    print(fd_meiduo)
    fd_meiduo2 = FDFS_Client_Meiduo()
    print(fd_meiduo2)
