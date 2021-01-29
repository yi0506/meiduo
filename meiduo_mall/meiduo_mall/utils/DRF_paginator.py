# -*- coding: UTF-8 -*-
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from meiduo_mall.utils import constants


class MeiduoAdminPaginator(PageNumberPagination):
    """自定义分页器"""
    page_size_query_param = 'pagesize'
    max_page_size = constants.ADMIN_USER_LIST_LIMIT

    def get_paginated_response(self, data):
        """自定义分页结果返回的数据形式"""
        return Response({
            'count': self.page.paginator.count,  # 总数量
            'lists': data,  # 用户数据
            'page': self.page.number,  # 当前页数
            'pages': self.page.paginator.num_pages,  # 总页数
            'pagesize': self.page_size  # 后端指定的页容量

        })


class MeiduoAdminSPUPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_SPU_LIST_LIMIT


class MeiduoAdminSKUPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_SKU_LIST_LIMIT


class MeiduoAdminOptionsPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_OPTIONS_LIST_LIMIT


class MeiduoAdminChannelsPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_CHANNEL_LIST_LIMIT


class MeiduoAdminBrandsPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_BRAND_LIST_LIMIT


class MeiduoAdminImagesPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_IMAGE_LIST_LIMIT


class MeiduoAdminOrdersPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_ORDER_LIMIT


class MeiduoAdminPermissionPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_PERMISSION_LIMIT


class MeiduoAdminGroupPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_PERMISSION_LIMIT


class MeiduoAdminAdministratorPaginator(MeiduoAdminPaginator):
    """自定义分页器"""
    max_page_size = constants.ADMIN_ADMINISTRATOR_LIMIT


if __name__ == '__main__':
    pass
