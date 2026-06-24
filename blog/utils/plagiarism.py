import re
from blog.models import Blog

def plagiarism_check(new_text):
    def tokenize(text):
        return set(re.findall(r"\w+", text.lower()))

    new_tokens = tokenize(new_text)
    if not new_tokens:
        return 0.0

    max_similarity = 0.0
    for old_text in Blog.objects.values_list("content", flat=True):
        old_tokens = tokenize(old_text)
        if not old_tokens:
            continue

        similarity = len(new_tokens & old_tokens) / len(new_tokens | old_tokens)
        max_similarity = max(max_similarity, similarity)

    return round(max_similarity * 100, 2)
