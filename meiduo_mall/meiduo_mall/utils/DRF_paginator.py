# -*- coding: UTF-8 -*-
from rest_framework.pagination import PageNumberPagination


class UserPaginator(PageNumberPagination):
    """自定义分页器"""
    page_query_param = 'pagesize'
    max_page_size = 10


if __name__ == '__main__':
    pass
