import secrets
import string

def generate_password(length=16, use_upper=True, use_lower=True, use_nums=True, use_syms=False):
    chars = ""
    if use_lower:
        chars += string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_nums:
        chars += string.digits
    if use_syms:
        chars += string.punctuation

    if not chars:
        chars = string.ascii_lowercase

    return ''.join(secrets.choice(chars) for _ in range(length))
