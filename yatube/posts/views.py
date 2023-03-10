from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post, User
from .utils import get_page


def index(request):
    posts = Post.objects.select_related('group', 'author')
    context = {
        'page_obj': get_page(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_list(request, group_name):
    group = get_object_or_404(Group, slug=group_name)
    posts = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': get_page(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    context = {
        'author': author,
        'page_obj': get_page(request, posts),
        'posts_count': posts.count(),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    chosen_post = get_object_or_404(Post, pk=post_id)
    comments = chosen_post.comments.all()
    form = CommentForm(
        request.POST or None,
    )
    context = {
        'chosen_post': chosen_post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    new_post = form.save(commit=False)
    new_post.author = request.user
    new_post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    chosen_post = get_object_or_404(Post, pk=post_id)
    if request.user != chosen_post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=chosen_post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    # Получите пост и сохраните его в переменную post.
    chosen_post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = chosen_post
        comment.save()
    return redirect('posts:post_detail', post_id)
