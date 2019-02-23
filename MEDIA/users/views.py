from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Article, Tag, Target, Comment
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


def profile_change(user, post, alerts):
	username = post.get('username', None)
	firstname = post.get('firstname', None)
	lastname = post.get('lastname', None)
	email = post.get('email', None)
	oldpass = post.get('oldpass', None)
	newpass = post.get('newpass', None)

	if username:
		user.username = username
		alerts['success'].append('Вы успешно изменили логин')

	if firstname:
		user.first_name = firstname
		alerts['success'].append('Вы успешно изменили имя')

	if lastname:
		user.last_name = lastname
		alerts['success'].append('Вы успешно изменили фамилию')

	if email:
		user.email = email
		alerts['success'].append('Вы успешно изменили эл. почту')

	if oldpass and newpass and user.check_password(oldpass):
		user.set_password(newpass)
		alerts['success'].append('Вы успешно изменили пароль')

	if len(alerts):
		user.save()

	return alerts


def add_article(user, post, alerts):
	title = post.get('title', None)
	short_text = post.get('short_text', None)
	full_text = post.get('full_text', None)
	tags = post.get('tags', None)

	if title and short_text and full_text and tags:
		try:
			article = Article.objects.get(
				title=title,
				author=user
			)
			alerts['danger'].append('Такая статья уже есть')
		except Article.DoesNotExist:
			article = Article.objects.create(
				title=title,
				legend=short_text,
				description=full_text,
				author=user
			)

			article.save()
			tags = tags.replace(" ", "").split(',')
			for tag in tags:
				try:
					t = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					t = Tag.objects.create(name=tag)
					t.save()
				article.tags.add(t)

			alerts['success'].append("Статья " + title + " успешно добавлена")
	elif post.get('form_add', None):
		alerts['danger'].append('Введите все данные')

	return alerts


def change_article(user, post, alerts):
	id = post.get('id_article', None)
	title = post.get('change_title', None)
	legend = post.get('change_legend', None)
	description = post.get('change_description', None)
	tags_str = post.get('change_tags', None)

	if id and title and legend and description and tags_str:
		try:
			article = Article.objects.get(pk=id, author=user)
			article.title = title
			article.legend = legend
			article.description = description
			article.save()
			tags = []
			[tags.append(item) for item in tags_str.replace(' ', '').split(',') if item]
			article.tags.clear()
			print(tags)

			for tag in tags:
				try:
					t = Tag.objects.get(name=tag)
				except Tag.DoesNotExist:
					t = Tag.objects.create(name=tag)
					t.save()
				article.tags.add(t)

			alerts['success'].append("Вы отредактировали статью " + title)
		except Article.DoesNotExist:
			alerts['danger'].append('У вас не достаточно прав чтобы исправить эту статью')
	elif post.get('form_change', None):
		alerts['danger'].append('Неправильные данные')

	return alerts


def add_target(user, post, alerts):
	title = post.get('title_target', None)
	description = post.get('short_target', None)
	price = post.get('price', None)

	if title and description and price:
		try:
			Target.objects.get(
				title=title,
				author=user
			)
			alerts['danger'].append('У вас уже есть такая же задача или похожая, измените её')
		except Target.DoesNotExist:
			target = Target.objects.create(
				title=title,
				description=description,
				price=price,
				currency="RUB",
				author=user
			)
			target.save()
			alerts['success'].append("Вы добавили задачу, которую надо выполнить")
	elif post.get('add_target', None):
		alerts['danger'].append("Введите корректные данные")

	return alerts


def user_page(request, id=None):
	section = request.GET.get('section', 'profile')
	alerts = {
		'success': [],
		'danger': []
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
			alerts = profile_change(user, r, alerts)

			# Made article
			alerts = add_article(user, r, alerts)

			# Edit article
			alerts = change_article(user, r, alerts)

			# Made target
			alerts = add_target(user, r, alerts)
			print(alerts)

	else:
		return redirect('/')

	articles = Article.objects.filter(author__id=sid)
	targets = Target.objects.filter(author__id=sid)

	return render(request, 'users/index.html', context={
		'user': user,
		'section': section,
		'header': header_data,
		'alerts': alerts,
		'articles': articles,
		'targets': targets
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
