from django.test import TestCase
import random
import string
import re


print(re.search(r'^[\d]{3}$', '1a3'))
print(''.join(random.choices(string.digits, k=5)))
