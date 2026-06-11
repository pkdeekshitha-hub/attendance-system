import os
from urllib.parse import urlparse

url = urlparse(os.environ.get('MYSQL_PUBLIC_URL', ''))

class Config:
    MYSQL_HOST = url.hostname
    MYSQL_USER = url.username
    MYSQL_PASSWORD = url.password
    MYSQL_DB = url.path.lstrip('/')
    MYSQL_PORT = url.port or 3306
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'supersecretkey123')
    JWT_ACCESS_TOKEN_EXPIRES = False