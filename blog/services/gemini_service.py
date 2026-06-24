from google import genai
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Tried in order. If one model is unavailable / quota-exhausted / deprecated,
# the next one is attempted automatically before falling back to a template.
MODEL_FALLBACK_ORDER = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash-preview",
]


def _build_prompt(topic, language, personalization_context=""):
    return f"""
Write a detailed blog article on "{topic}" in {language} language.

Include:
- Introduction
- Subheadings
- Examples
- Conclusion

Write in simple and clear language.
{personalization_context}
"""


def _offline_fallback_blog(topic, language):
    """
    Used only when every Gemini model attempt fails (quota exhausted,
    network issue, deprecated model, etc). Keeps the agentic pipeline
    (plagiarism check, rewrite decision, logging) working end-to-end
    so the rest of the system can still be demoed live.
    """
    return f"""Introduction

{topic} is a subject that has grown increasingly relevant in recent times. Understanding its core ideas helps in applying them effectively in real-world situations.

Why {topic} Matters

Many learners and professionals are turning their attention to {topic} because of its practical impact and the value it brings to everyday problem-solving.

Key Points to Know

There are several aspects of {topic} worth exploring, including its fundamental concepts, common use cases, and the benefits it offers to those who study it carefully.

Examples

A simple way to understand {topic} is to look at how it is applied in familiar, everyday scenarios. This makes the underlying ideas easier to grasp and remember.

Conclusion

In summary, {topic} is a valuable area to explore. With consistent learning and practice, anyone can build a strong understanding of it over time.

(Note: generated language requested was {language}.)
"""


def generate_blog_from_topic(topic, language="English", personalization_context=""):
    prompt = _build_prompt(topic, language, personalization_context)
    last_error = None

    for model_name in MODEL_FALLBACK_ORDER:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and getattr(response, "text", None):
                return response.text
        except Exception as e:
            last_error = e
            continue

    # All API attempts failed (quota/network/deprecated model etc.)
    # Fall back to a locally generated draft so the app stays usable.
    print(f"[gemini_service] All Gemini model attempts failed, using offline fallback. Last error: {last_error}")
    return _offline_fallback_blog(topic, language)