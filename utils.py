from hashlib import sha256
from datetime import datetime


def hash_password(password, secret_key):
    return sha256(f'{secret_key}{password}'.encode()).hexdigest()


def create_session_token(secret_key):
    now = datetime.now()
    return sha256(f'{secret_key}{now}'.encode()).hexdigest()
