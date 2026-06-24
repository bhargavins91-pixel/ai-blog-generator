# blog/agents/personalization_agent.py

from collections import Counter
import re

STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "to", "for", "with",
    "is", "are", "how", "what", "why", "guide", "introduction", "blog",
    "about", "your", "you", "it", "this", "that", "as", "by", "from"
}

MIN_PAST_BLOGS_FOR_PERSONALIZATION = 1


def _extract_keywords(topics):
    """Pulls out recurring meaningful words from a list of past topics."""
    words = []
    for topic in topics:
        for word in re.findall(r"[a-zA-Z]+", topic.lower()):
            if word not in STOPWORDS and len(word) > 2:
                words.append(word)
    return words


def build_user_profile(user, blog_model):
    """
    Looks at a user's past blogs and builds a lightweight profile:
    - preferred language (most frequently used)
    - recurring topic keywords (interests)
    - number of past blogs (for confidence)

    `blog_model` is passed in (instead of imported directly) to avoid
    circular imports between agents and models.
    """
    past_blogs = blog_model.objects.filter(author=user).order_by("-created_at")[:20]

    if not past_blogs:
        return {
            "has_history": False,
            "preferred_language": "English",
            "interests": [],
            "past_count": 0,
        }

    languages = [b.language for b in past_blogs if b.language]
    topics = [b.topic for b in past_blogs if b.topic]

    preferred_language = Counter(languages).most_common(1)[0][0] if languages else "English"
    keywords = _extract_keywords(topics)
    top_interests = [word for word, _ in Counter(keywords).most_common(5)]

    return {
        "has_history": True,
        "preferred_language": preferred_language,
        "interests": top_interests,
        "past_count": len(past_blogs),
    }


def personalize_prompt_context(profile):
    """
    Turns a user profile into a short instruction snippet that gets
    appended to the blog-generation prompt, nudging tone/angle based
    on the user's writing history without overriding their explicit topic.
    """
    if not profile["has_history"] or profile["past_count"] < MIN_PAST_BLOGS_FOR_PERSONALIZATION:
        return ""

    interests_str = ", ".join(profile["interests"]) if profile["interests"] else "general topics"

    return (
        f"\nPersonalization context (use lightly, do not force it): "
        f"This author has previously written {profile['past_count']} blog(s), "
        f"often around themes like {interests_str}. "
        f"Where natural, relate the new topic back to these interests."
    )