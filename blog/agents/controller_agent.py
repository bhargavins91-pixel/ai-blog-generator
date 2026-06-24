# blog/agents/controller_agent.py

from ..services.gemini_service import generate_blog_from_topic
from ..utils.plagiarism import plagiarism_check
from .personalization_agent import build_user_profile, personalize_prompt_context

PLAGIARISM_THRESHOLD = 30  # percentage

def run_agentic_flow(topic, language="English", user=None):

    agent_logs = []

    agent_logs.append("[Controller Agent] Agentic flow started")

    # Personalization Agent
    personalization_context = ""
    if user is not None:
        from ..models import Blog  # local import avoids circular import at module load time
        profile = build_user_profile(user, Blog)

        if profile["has_history"]:
            agent_logs.append(
                f"[Personalization Agent] Found {profile['past_count']} past blog(s) — "
                f"preferred language: {profile['preferred_language']}, "
                f"interests: {', '.join(profile['interests']) if profile['interests'] else 'none detected yet'}"
            )
            personalization_context = personalize_prompt_context(profile)
        else:
            agent_logs.append(
                "[Personalization Agent] No past blogs found — generating without personalization"
            )

    # Writer Agent
    agent_logs.append(f"[Writer Agent] Generating blog in {language}")
    blog = generate_blog_from_topic(topic, language, personalization_context)

    # Plagiarism Agent
    plagiarism_score = plagiarism_check(blog)

    agent_logs.append(
        f"[Plagiarism Agent] Similarity score: {plagiarism_score}%"
    )

    # Decision Agent
    if plagiarism_score > PLAGIARISM_THRESHOLD:

        agent_logs.append(
            "[Decision Agent] High plagiarism → rewriting content"
        )

        blog = generate_blog_from_topic(
            f"Rewrite and improve this content:\n{blog}",
            language,
            personalization_context
        )

    else:
        agent_logs.append(
            "[Decision Agent] Plagiarism acceptable → no rewrite needed"
        )

    agent_logs.append("[Controller Agent] Flow completed")

    return blog, agent_logs