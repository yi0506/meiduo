from django.test import TestCase
from datetime import datetime

obj_date = datetime.strptime('2019-11-22', '%Y-%m-%d')
print(obj_date)
str_date = datetime.strftime(obj_date, '%Y:%m:%d')
str_date2 = obj_date.strftime('%Y:%m:%d')
print(str_date2, 'str2')
print(str_date)
# Create your tests here.
