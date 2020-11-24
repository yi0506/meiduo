from django.test import TestCase
import random
import string
# Create your tests here.

print(''.join(random.choices(string.digits, k=5)))