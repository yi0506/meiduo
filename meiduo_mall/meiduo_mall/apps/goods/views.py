from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage  # Paginator为分页器，EmptyPage为分页器的异常
from django.utils import timezone  # 处理时间的工具
from datetime import datetime
from logging import getLogger

from goods.models import GoodsCategory, SKU, GoodsVisitCount
from meiduo_mall.utils.method_package import get_categories, get_breadcrumb
from meiduo_mall.utils import constants
from meiduo_mall.utils.response_code import RETCODE, err_msg


logger = getLogger('django')


class DetailVisitView(View):
    """统计商品访问量"""
    def post(self, request, category_id):
        """处理统计商品访问量的逻辑"""
        # 接收、校验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('category_id不存在')
        # 获取当天的日期
        t = timezone.localtime()
        # 获取当天的时间字符串
        # today_str = "%d-%02d-%02d" % (t.year, t.month, t.day)
        today_str = "{:d}-{:0>2d}-{:0>2d}".format(t.year, t.month, t.day)
        # 将时间字符串转为时间对象datetime，为了与DateField字段类型匹配
        today_date = datetime.strptime(today_str, '%Y-%m-%d')
        # 统计指定分类商品的访问量
        # GoodsVisitCount.objects.filter(data='当天日期', category_id=category.id)
        # 判断当天中指定的分类商品对应的记录是否存在
        try:
            # 如果查询到记录，直接获取到记录对应的对象
            counts_obj = GoodsVisitCount.objects.get(date=today_date, category=category)
        except GoodsVisitCount.DoesNotExist:
            # 如果查询不到记录，则新建一条记录对应的对象
            counts_obj = GoodsVisitCount()
        try:
            # 更新该条记录
            counts_obj.category = category
            counts_obj.count += 1  # count默认为0
            counts_obj.date = today_date
            counts_obj.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('统计失败')
        else:
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK]})


class DetailView(View):
    """商品详情页"""
    def get(self, request, sku_id):
        """提供商品详情页"""
        # 接收、校验参数
        try:
            # 查询商品sku信息
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}
        for s in skus:
            # 获取sku的规格参数
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return
        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs
        }
        return render(request, 'detail.html', context)


class HotGoodsView(View):
    """热销排行视图"""
    def get(self, request, category_id):
        """查询列表页热销排行数据"""
        try:
            skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id错误')
        hot_skus = []
        for sku in skus:
            sku_dict = {
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            }
            hot_skus.append(sku_dict)
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': err_msg[RETCODE.OK], 'hot_skus': hot_skus})


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        # 获取商品排序规则
        sort = request.GET.get('sort', 'default')
        # 根据sort选择排序字段
        if sort == 'price':  # 按照价格从低到高排序
            sort_field = 'price'
        elif sort == 'hot':  #
            sort_field = '-sales'  # 按照销量从高到低排序
        else:  # 其他情况视为 默认情况 'default'
            sort = 'default'  # sort 为其他值时，如 'comprehensive'， 则设为 'default'
            sort_field = 'create_time'
        try:
            # 校验category_id，防止出现 category_id > 商品类别数量
            category = GoodsCategory.objects.get(id=category_id)  # category为三级类别
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('参数category_id错误')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航： 一级 -> 二级 ->三级
        breadcrumb = get_breadcrumb(category)
        # 分页查询和排序：category查询sku，一查多
        try:
            skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('查询条件错误')
        # 创建分页器
        # Paginator('要分页的记录', '每页记录的条数')
        paginator = Paginator(skus, constants.RECORDS_NUM_PER_PAGE)  # 把skus进行分页，每页5条记录
        # 获取用户要看的那一个记录
        try:
            page_skus = paginator.page(page_num)  # 获取到page_num页中的5条记录
        # 如果用户输入的page_num是否超过总页数，捕获异常
        except EmptyPage:
            return http.HttpResponseNotFound('Empty Page')
        # 获取总页数，前端分页插件使用
        total_pages = paginator.num_pages
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_pages': total_pages,
            'page_num': page_num,
            'sort': sort,
            'category_id': category_id,
        }
        return render(request, 'list.html', context)

