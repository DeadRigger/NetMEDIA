from django.contrib import admin
from .models import *


@admin.register(Article, Tag, Comment, Target)
class AdminSite(admin.ModelAdmin):
    pass
