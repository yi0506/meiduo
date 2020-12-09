from django.db import models
from django.contrib.auth.models import AbstractUser

from meiduo_mall.utils.models import BaseModel


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='province_addresses', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='city_addresses', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='district_addresses', verbose_name='区')
    place = models.CharField(max_length=50, verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20, null=True, blank=True, default='', verbose_name='固定电话')
    email = models.CharField(max_length=30, null=True, blank=True, default='', verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        # 定义表的排序方式
        # 语法格式：'-字段名': 倒序，  '字段名': 升序
        # 字段名为 按照哪个字段排序，"-" 表示升序还是降序
        ordering = ['-update_time']


class User(AbstractUser, BaseModel):
    """自定义用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")  # admin站点中，该字段信息显示为手机号
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 外键指向一个模型类对象，因此，对外键赋值，要赋值 模型类对象 或者 模型类对象_id
    # 如果赋值 模型类对象 ，Django会自动获取 该模型类对象的主键id，并将主键id添加到对应 模型类对象_id 的字段中
    default_address = models.ForeignKey('Address', related_name='users', null=True, blank=True,
                                        on_delete=models.SET_NULL, verbose_name='默认地址')
    class Meta:
        db_table = 'tb_users'  # 自定义数据表名，在mysql中显示的表名
        verbose_name = "用户"  # 自定义在admin站点中显示的表名
        verbose_name_plural = verbose_name  # verbose_name的复数形式显示

    def __str__(self):
        """
        输出该对象的显示信息，
            如在终端打印时，
            在debug模式下，变量显示的名称，
            在admin后台站点显示的名称
        """
        return self.username
