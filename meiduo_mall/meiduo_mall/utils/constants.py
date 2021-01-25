# 图形验证码有效期，单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码有效期，单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 短信模板
SEND_SMS_TEMPLATE_ID = 1

# 60s内是否重复发送的标记
SEND_SMS_CODE_INTERVAL = 60

# 记住登录的状态保持时间
REMEMBERED_EXPIRES = 3600

# openid过期时间
OPENID_EXPIRES = 600

# 邮件验证链接有效期：一天
VERIFY_EMAIL_TOKEN_EXPIRES = 60 * 60 * 24

# 用户地址上限
USER_ADDRESS_COUNTS_LIMIT = 20

# 省市区联动数据缓存过期时间
PROVINCE_CITY_DISTRICT_EXPIRES = 3600

# 商品列表页每页显示记录的条数
RECORDS_NUM_PER_PAGE = 5

# 个人中心显示浏览记录的条数
USER_CENTER_HISTORY_COUNT = 4

# 未登录用户购物车数据保存时间
ANONYMOUS_USER_CART_EXPIRES = 1200

# 指定运费
ORDERS_FREIGHT_COST = 10.00

# 每页展示订单数量
ORDERS_LIST_LIMIT = 5

# 展示的评价数量
COMMENTS_LIST_LIMIT = 30

# 后台每页显示的用户数量
ADMIN_USER_LIST_LIMIT = 2

# 后台SPU每页显示数量
ADMIN_SPU_LIST_LIMIT = 5
