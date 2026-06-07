import os

class Config:
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'attendance_db')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'supersecretkey123')
    JWT_ACCESS_TOKEN_EXPIRES = False