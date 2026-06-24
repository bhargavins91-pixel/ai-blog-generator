from django.contrib import admin
from .models import Blog, Review, Rating

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("topic", "author", "plagiarism_score", "created_at")
    search_fields = ("topic", "author__username")
    list_filter = ("created_at",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "created_at")
    search_fields = ("blog__topic", "user__username")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("blog", "user", "stars")
    list_filter = ("stars",)
