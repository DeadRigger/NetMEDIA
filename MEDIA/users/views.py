from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Article, Tag
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect

import time

header_data = {
	'user_tabs': [
		{
			'name': 'profile',
			'ru': 'Профиль',
			'href': '/profile/?section=profile',
			'html': 'users/profile.html'
		},
		{
			'name': 'articles',
			'ru': 'Статьи',
			'href': '/profile/?section=articles',
			'html': 'users/articles.html'
		},
		{
			'name': 'target',
			'ru': 'Задачи',
			'href': '/profile/?section=target',
			'html': 'users/target.html'
		},
		{
			'name': 'comments',
			'ru': 'Комментарии',
			'href': '/profile/?section=comments',
			'html': 'users/comments.html'
		},
		{
			'name': 'logout',
			'ru': 'Выход',
			'href': '/logout/'
		},
	],
	'social': ['vk', 'twitter', 'google', 'instagram', 'facebook', 'telegram'],
}


def index(request):
	user = None
	id = request.session.get('_auth_user_id', None)
	if id is not None:
		user = User.objects.get(id=id)

	if user is None and request.method == "POST":
		user = authenticate(username=request.POST['login'], password=request.POST['pass'])
		if user is not None:
			login(request, user)

	articles = Article.objects.all()

	return render(request, 'index.html', context={
		'articles': articles,
		'user': user,
		'header': header_data
	})


def profile_change(user, post):
	alerts = []
	if post.get('username', None):
		user.username = post['username']
		alerts.append('логин')

	if post.get('firstname', None):
		user.first_name = post['firstname']
		alerts.append('имя')

	if post.get('lastname', None):
		user.last_name = post['lastname']
		alerts.append('фамилию')

	if post.get('email', None):
		user.email = post['email']
		alerts.append('эл. почту')

	if post.get('oldpass', None) and post.get('newpass', None) and user.check_password(post.get('oldpass', None)):
		user.set_password(post['newpass'])
		alerts.append('пароль')

	if len(alerts):
		user.save()

	return alerts


def add_article(user, post):
	alerts = {
		'success': None,
		'danger': None
	}
	if post.get('title', None) and post.get('short_text', None) and post.get('full_text', None) and post.get('tags', None):
		try:
			article = Article.objects.get(
				title=post['title'],
				author=user
			)
			alerts['danger'] = 'Такая статья уже есть'
		except Article.DoesNotExist:
			article = Article.objects.create(
				title=post['title'],
				legend=post['short_text'],
				description=post['full_text'],
				author=user
			)

			article.save()
			tags = post['tags'].replace(" ", "").split(',')
			for tag in tags:
				try:
					t = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					t = Tag.objects.create(name=tag)
					t.save()
				article.tags.add(t)

			alerts['success'] = post['title']
	else:
		alerts['danger'] = 'Введите все данные'

	return alerts


def user_page(request, id=None):
	section = request.GET.get('section', 'profile')
	user_alerts = []
	art_alerts = {
		'success': None,
		'danger': None
	}

	sid = request.session.get('_auth_user_id', None)
	if sid is not None:
		user = User.objects.get(id=sid)
		if id and id != sid:
			try:
				user = User.objects.get(id=id)
			except ObjectDoesNotExist:
				raise Http404("No MyModel matches the given query.")

		if request.method == "POST" and (id is None or sid == id):
			r = request.POST

			# Change profile
			user_alerts = profile_change(user, r)

			# Made article
			art_alerts = add_article(user, r)
			print(art_alerts)

	else:
		return redirect('/')

	articles = Article.objects.filter(author__id=sid)

	return render(request, 'users/index.html', context={
		'user': user,
		'section': section,
		'header': header_data,
		'alerts': {
			'user': user_alerts,
			'article': art_alerts
		},
		'articles': articles,
	})


def tag_page(request):
	tag = request.GET.get("tag", None)
	if tag is not None:
		articles = Article.objects.filter(tags__name=tag)
	else:
		articles = Article.objects.all()

	user = None
	id = request.session.get('_auth_user_id', None)
	if id is not None:
		user = User.objects.get(id=id)

	if user is None and request.method == "POST":
		user = authenticate(username=request.POST['login'], password=request.POST['pass'])
		if user is not None:
			login(request, user)

	return render(request, 'index.html', context={
		'articles': articles,
		'user': user,
		'header': header_data
	})


def logout_page(request):
	logout(request)
	return redirect('/')
