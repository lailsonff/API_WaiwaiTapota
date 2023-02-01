import os
from random import choice
from string import ascii_letters, digits, ascii_uppercase, ascii_lowercase

random = ascii_letters + digits + ascii_uppercase + ascii_lowercase
secret_key = ''.join(choice(random) for i in range(48))
config = dict(
    DB_URL=os.environ.get('DB_URL', "mongodb://mongo"),
    DB_PORT=os.environ.get('DB_PORT', 27017),
    DB_NAME=os.environ.get('DB_NAME', "waiwaitapota"),
    DB_USER=os.environ.get('DB_USER', ""),
    DB_PASSWORD=os.environ.get('DB_PASSWORD', ""),
    SECRET_KEY=os.environ.get('SECRET_KEY', secret_key),
    ACCESS_TOKEN_EXPIRES=os.environ.get('ACCESS_TOKEN_EXPIRES', 1),
    REFRESH_TOKEN_EXPIRES=os.environ.get('REFRESH_TOKEN_EXPIRES', 30),
    REDIS_HOST=os.environ.get('REDIS_HOST', 'redis'),
    REDIS_DB=os.environ.get('REDIS_DB', ''),
    REDIS_PORT=os.environ.get('REDIS_PORT', 6379)
)