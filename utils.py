import string
import random

BASE62 = string.ascii_letters + string.digits

def generate_short_code(length: int = 6) -> str:
    return ''.join(random.choices(BASE62, k=length))