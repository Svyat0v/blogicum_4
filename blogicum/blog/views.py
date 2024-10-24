
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required


from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserProfileForm
from .managers import get_paginator, get_queryset


def index(request):
    """Отображение на главной странице."""
    posts_list = get_queryset()
    page_number = request.GET.get('page', 1)
    page_obj = get_paginator(page_number, posts_list)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Страница отдельной публикации."""
    post = get_object_or_404(
        Post,
        id=post_id
    )
    if post.author != request.user:
        post = get_object_or_404(get_queryset(), id=post_id)
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_queryset(manager=category.posts)
    page_number = request.GET.get('page', 1)
    page_obj = get_paginator(page_number, posts)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    """Создание публикации."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)

    context = {'form': form, 'post': post}
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, post_id):
    """Удаление публикации."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление комментария публикации."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария публикации."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return HttpResponseForbidden(
            "У вас нет прав для редактирования этого комментария."
        )

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post_id)

    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария публикации."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)

    if request.user != comment.author:
        return HttpResponseForbidden(
            "У вас нет прав для удаления этого комментария."
        )

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {'comment': comment})


# Мой код
@login_required
def profile_edit(request):
    """Редактирование пользователя."""
    form = UserProfileForm(request.POST or None, instance=request.user)

    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/user.html', {'form': form})


def profile(request, username):
    """Профиль пользователя."""
    user = get_object_or_404(User, username=username)
    if request.user == user:
        posts = user.posts.all().order_by('-pub_date')
    else:
        posts = get_queryset(
            manager=user.posts.all(),
            filters=True
        ).order_by('-pub_date')
    page_number = request.GET.get('page', 1)
    page_obj = get_paginator(page_number, posts)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)
