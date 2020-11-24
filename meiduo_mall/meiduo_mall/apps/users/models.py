from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """自定义用户模型类"""

    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")  # admin站点中，该字段信息显示为手机号

    class Meta:
        db_table = 'tb_users'  # 自定义数据表名，在mysql中显示的表名
        verbose_name = "用户"  # 自定义在admin站点中显示的表名
        verbose_name_plural = verbose_name  # verbose_name的复数形式显示

    def __str__(self):
        """在调试阶段，打印到终端时，定义每个数据对象的显示信息"""
        return self.username