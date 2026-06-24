
from django.db import models
from django.contrib.auth.models import User

# -------------------------
# BLOG MODEL
# -------------------------
class Blog(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    topic = models.CharField(max_length=200)

    content = models.TextField()

    plagiarism_score = models.FloatField(default=0)

    agent_log = models.TextField(blank=True)

    language = models.CharField(max_length=50, default="English")

    generation_time = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic


# -------------------------
# REVIEW MODEL
# -------------------------
class Review(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review"


# -------------------------
# RATING MODEL
# -------------------------
class Rating(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.blog.topic} - {self.stars} stars"
