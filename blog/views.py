from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from blog.agents.controller_agent import run_agentic_flow
from blog.utils.plagiarism import plagiarism_check
from .models import Blog, Review, Rating

import re
import time

# -------------------------------------------------
# AI BLOG GENERATION (AGENTIC AI)
# -------------------------------------------------
def generate_blog(topic, language):
    """
    Calls Agentic AI controller and returns:
    - generated blog content
    - agent execution logs
    """

    content, agent_logs = run_agentic_flow(topic, language)

    # Remove markdown headings like ###, ##, #
    content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)

    # Remove bold and italic markers ** and *
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = re.sub(r'\*(.*?)\*', r'\1', content)

    # Remove horizontal lines ---
    content = re.sub(r'-{3,}', '', content)

    # Remove stray markdown symbols
    content = re.sub(r'[`>#]', '', content)

    # Fix multiple new lines
    content = re.sub(r'\n\s*\n+', '\n\n', content)

    # Remove extra spaces
    content = re.sub(r'[ \t]+', ' ', content)

    return content.strip(), agent_logs


# -------------------------------------------------
# LANDING PAGE
# -------------------------------------------------
def landing(request):
    return render(request, "blog/landing.html")


# -------------------------------------------------
# HOME VIEW
# -------------------------------------------------
@login_required
def home(request):
    sort = request.GET.get("sort", "new")

    blogs = Blog.objects.annotate(
        avg_rating=Avg("ratings__stars")
    ).order_by("-created_at" if sort == "new" else "created_at")

    if request.method == "POST":
        topic = request.POST.get("topic")
        language = request.POST.get("language", "English")

        start_time = time.time()
        content, agent_logs = run_agentic_flow(topic, language, user=request.user)
        elapsed_time = round(time.time() - start_time, 2)

        blog = Blog.objects.create(
            author=request.user,
            topic=topic,
            content=content,
            plagiarism_score=plagiarism_check(content),
            agent_log="\n".join(agent_logs),
            language=language,
            generation_time=elapsed_time
        )

        return redirect("blog_detail", blog.id)

    return render(request, "blog/home.html", {
        "blogs": blogs,
        "sort": sort
    })


# -------------------------------------------------
# BLOG DETAIL VIEW
# -------------------------------------------------
@login_required
def blog_detail(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":

        # Save review comment
        if "comment" in request.POST:
            Review.objects.create(
                blog=blog,
                user=request.user,
                comment=request.POST.get("comment")
            )

        # Save rating
        if "stars" in request.POST:
            Rating.objects.update_or_create(
                blog=blog,
                user=request.user,
                defaults={"stars": int(request.POST.get("stars"))}
            )

        return redirect("blog_detail", blog.id)

    avg_rating = blog.ratings.aggregate(avg=Avg("stars"))["avg"] or 0

    return render(request, "blog/blog_detail.html", {
        "blog": blog,
        "avg_rating": round(avg_rating, 1),
    })

@login_required
def dashboard(request):
    total_blogs = Blog.objects.count()

    avg_generation_time = Blog.objects.aggregate(
        Avg("generation_time")
    )["generation_time__avg"] or 0

    avg_plagiarism = Blog.objects.aggregate(
        Avg("plagiarism_score")
    )["plagiarism_score__avg"] or 0

    avg_rating = Rating.objects.aggregate(
        Avg("stars")
    )["stars__avg"] or 0

    context = {
        "total_blogs": total_blogs,
        "avg_generation_time": round(avg_generation_time, 2),
        "avg_plagiarism": round(avg_plagiarism, 2),
        "avg_rating": round(avg_rating, 2),
    }

    return render(request, "blog/dashboard.html", context)