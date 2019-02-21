from django.db import models
from django.contrib.auth.models import User


class Tag(models.Model):
	name = models.CharField(max_length=255, unique=True)

	def __str__(self):
		return self.name


class Article(models.Model):
	title = models.CharField(max_length=100)
	legend = models.CharField(max_length=300)
	description = models.TextField()
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	time_published = models.DateTimeField(auto_now_add=True)
	tags = models.ManyToManyField(
		Tag,
		related_name="articles",
		related_query_name="article",
		db_table="user_article_tags"
	)

	def __str__(self):
		return self.title

	class Meta:
		ordering = ["-time_published"]
