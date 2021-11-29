from datetime import datetime
from hashlib import sha256


def hash_password(password, secret_key):
    return sha256(f"{password}{secret_key}".encode()).hexdigest()


def create_session_token(secret_key):
    now = datetime.now()
    return sha256(f"{now}{secret_key}".encode()).hexdigest()
