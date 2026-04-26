from cryptography.fernet import Fernet

def get_fernet(secret_key: str) -> Fernet:
    key = secret_key.encode() if isinstance(secret_key, str) else secret_key
    return Fernet(key)

def encrypt(value: str, secret_key: str) -> str:
    f = get_fernet(secret_key)
    return f.encrypt(value.encode()).decode()

def decrypt(encrypted: str, secret_key: str) -> str:
    f = get_fernet(secret_key)
    return f.decrypt(encrypted.encode()).decode()
