from django.test import TestCase

# Create your tests here.
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


serializer = Serializer(secret_key='Signature_key', expires_in=600)

data = {'openid': '94F263BE6A881C997259199C7A3EB757', 'user_id': '12345678'}

token = serializer.dumps(data)
print(token.decode())

deserilizer = Serializer(secret_key='Signature_key', expires_in=300)

data = deserilizer.loads(token)
print(data)