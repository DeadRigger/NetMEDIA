from django.contrib import admin
from .models import Article, Tag


@admin.register(Article, Tag)
class AdminSite(admin.ModelAdmin):
    pass
