import regex as re
import math as math
from collections import Counter

def normalize_vn_string(s):
    s = re.sub(r'[^\p{L}\p{N} \n]+', '', s)
    s = re.sub(r'[\s]+',' ', s)
    s = s.strip()
    s = s.lower()
    return s

def cosine_similarity(vec1, vec2):
    vec1 = Counter(vec1)
    vec2 = Counter(vec2)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum(vec1[x] * vec2[x] for x in intersection)
    sum1 = sum(vec1[x] ** 2 for x in vec1.keys())
    sum2 = sum(vec2[x] ** 2 for x in vec2.keys())
    denominator = math.sqrt(sum1) + math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator