from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import json
from . import settings


def get_sysdata(key=None):
    sysfile = str(settings.setup_dir /'config.json')
    with open(sysfile, 'r') as f:
        sysdata = json.loads(f.read())
    if key is None:
        return sysdata
    else:
        return sysdata[key]


def get_key(base=None) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=32,
        salt=b'K2?uY#I%K3n4',
        iterations=100000,
        backend=default_backend()
    )
    if base is None:
        sysdata = get_sysdata()
        security_key = sysdata['security_key']
    else:
        security_key = base
    key = base64.urlsafe_b64encode(kdf.derive(security_key.encode()))
    return key


current_key = get_key()

def encrypt(string: str, key=current_key) -> str:
    engine_ = Fernet(key)
    cipher = engine_.encrypt(string.encode())
    return cipher.decode()


def decrypt(cipher: str, key=current_key) -> str:
    engine_ = Fernet(key)
    bytes_ = engine_.decrypt(cipher.encode())
    return bytes_.decode()