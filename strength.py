import math
import re

def check_strength(password):
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_nums = bool(re.search(r'\d', password))
    has_syms = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    pool_size = sum([
        26 if has_lower else 0,
        26 if has_upper else 0,
        10 if has_nums else 0,
        32 if has_syms else 0
    ])

    entropy = len(password) * math.log2(pool_size) if pool_size > 0 else 0

    score = 0
    score += 10 if len(password) >= 8 else 0
    score += 20 if len(password) >= 12 else 0
    score += 15 if has_upper else 0
    score += 5 if has_lower else 0
    score += 15 if has_nums else 0
    score += 10 if has_syms else 0
    score += 25 if entropy > 60 else 0

    level = "强" if score >= 80 else "中" if score >= 60 else "弱"

    return {"score": min(score, 100), "level": level, "entropy": round(entropy, 2)}
